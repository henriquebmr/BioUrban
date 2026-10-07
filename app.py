from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, Usuario, Fazenda, Hortalica, RegistroHidrico
from datetime import datetime
import csv
import io
import numpy as np
from sklearn.linear_model import LinearRegression
import threading
import time
import random
import serial
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biourban_pro.db'
app.config['SECRET_KEY'] = 'chave-segura-biourban-2026'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# ==============================================================================
# CONFIGURAÇÃO DA COMUNICAÇÃO SERIAL (USB) COM O ESP32
# ==============================================================================
PORTA_SERIAL = 'COM3'
VELOCIDADE_BAUD = 9600
ID_FAZENDA_PADRAO = 1

# VARIÁVEIS GLOBAIS DE CONTROLE DO SENSOR
sensor_fisico_ativo = False
thread_usb = None
PLANTA_FOCO_ID = None

def ler_dados_usb():
    global sensor_fisico_ativo, PLANTA_FOCO_ID
    try:
        ser = serial.Serial(PORTA_SERIAL, VELOCIDADE_BAUD, timeout=1)
        print(f"\n[INFO] ✅ Lendo dados do BioUrban físico via {PORTA_SERIAL}\n")
        
        while True:
            if not sensor_fisico_ativo:
                time.sleep(1)
                continue
                
            if ser.in_waiting > 0:
                linha = ser.readline().decode('utf-8', errors='ignore').strip()
                try:
                    dados = json.loads(linha)
                    umidade = dados.get('umidade')
                    status = dados.get('status')
                    
                    if umidade is not None:
                        with app.app_context():
                            novo_registro = RegistroHidrico(
                                nivel_porcentagem=float(umidade),
                                data_leitura=datetime.now().strftime('%H:%M:%S'),
                                origem="sensor",
                                fazenda_id=ID_FAZENDA_PADRAO,
                                hortalica_id=PLANTA_FOCO_ID
                            )
                            db.session.add(novo_registro)
                            
                            nome_planta = "Nenhuma selecionada"
                            if PLANTA_FOCO_ID:
                                planta = db.session.get(Hortalica, PLANTA_FOCO_ID)
                                if planta:
                                    planta.umidade_atual = float(umidade)
                                    nome_planta = planta.nome
                                    
                            db.session.commit()
                            print(f"[USB] 🌱 {nome_planta}: Umidade = {umidade}% | Status: {status}")
                            
                except json.JSONDecodeError:
                    pass
            time.sleep(2)
            
    except serial.SerialException as e:
        print(f"\n[ERRO] ❌ Falha ao conectar na porta serial {PORTA_SERIAL}")
        print("Verifique se a porta está correta e se o Monitor Serial do Arduino IDE está FECHADO.\n")

thread_usb = threading.Thread(target=ler_dados_usb, daemon=True)
thread_usb.start()
# ==============================================================================

# --- CONTROLE GLOBAL DO SIMULADOR IOT EM SEGUNDO PLANO ---
simulador_ativo = False
simulador_thread = None
ADC_NO_AR = 3180
ADC_NA_AGUA = 1150

def rodar_simulacao(fazenda_id):
    global simulador_ativo, PLANTA_FOCO_ID
    while simulador_ativo:
        adc_simulado = random.randint(1400, 2945)
        pct = (ADC_NO_AR - adc_simulado) / (ADC_NO_AR - ADC_NA_AGUA) * 100.0
        porcentagem = round(max(0.0, min(100.0, pct)), 1)

        with app.app_context():
            novo = RegistroHidrico(
                nivel_porcentagem=porcentagem,
                data_leitura=datetime.now().strftime('%H:%M:%S'),
                origem="simulador",
                fazenda_id=fazenda_id,
                hortalica_id=PLANTA_FOCO_ID
            )
            db.session.add(novo)
            
            if PLANTA_FOCO_ID:
                planta = db.session.get(Hortalica, PLANTA_FOCO_ID)
                if planta:
                    planta.umidade_atual = porcentagem
                    
            db.session.commit()
        time.sleep(2)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))

with app.app_context():
    db.create_all()

@app.template_filter('dias_cultivo')
def dias_cultivo_filter(data_plantio_str):
    try:
        if not data_plantio_str: return 0
        data_plantio = datetime.strptime(data_plantio_str, '%Y-%m-%d').date()
        return (datetime.now().date() - data_plantio).days
    except: return 0

# --- ROTAS DE AUTENTICAÇÃO ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login inválido. Verifique suas credenciais.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        if not Usuario.query.filter_by(username=username).first():
            novo = Usuario(username=username, password=request.form.get('password'))
            db.session.add(novo); db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- DASHBOARD (LISTA DE UNIDADES) ---

@app.route('/', endpoint='dashboard')
@login_required
def dashboard():
    minhas_fazendas = Fazenda.query.filter_by(usuario_id=current_user.id).all()
    return render_template('dashboard.html', fazendas=minhas_fazendas)

@app.route('/add_fazenda', methods=['POST'])
@login_required
def add_fazenda():
    nome = request.form.get('nome')
    local = request.form.get('localizacao')
    if nome:
        nova = Fazenda(nome=nome, localizacao=local, usuario_id=current_user.id)
        db.session.add(nova); db.session.commit()
    return redirect(url_for('dashboard'))

# --- PÁGINA DA UNIDADE (GESTÃO + DUAL IA) ---

@app.route('/fazenda/<int:id>')
@login_required
def ver_fazenda(id):
    fazenda = db.session.get(Fazenda, id)
    if not fazenda or fazenda.usuario_id != current_user.id: return "Acesso Negado", 403
    
    global PLANTA_FOCO_ID
    filtro = request.args.get('filtro', 'Todos')
    hoje = datetime.now().date()
    contagem_variedades = {}
    total_ciclos, qtd_ativas = 0, 0
    previsoes_ia = {}

    stats = {
        'total_ativas': 0,
        'tempo_medio': 0,
        'total_h2o': 0,
        'media_h2o': 0,
        'filtro_atual': filtro,
        'previsoes': {},
        'insight_h2o': None
    }

    if PLANTA_FOCO_ID is None and len(fazenda.hortalicas) > 0:
        PLANTA_FOCO_ID = fazenda.hortalicas[0].id

    for h in fazenda.hortalicas:
        if h.status != 'Colhido':
            if h.ciclo_estimado:
                total_ciclos += h.ciclo_estimado
                qtd_ativas += 1
            contagem_variedades[h.nome] = contagem_variedades.get(h.nome, 0) + 1
            try:
                d_p = datetime.strptime(h.data_plantio, '%Y-%m-%d').date()
                passados = (hoje - d_p).days
                h.atrasada = passados > (h.ciclo_estimado or 0)
                h.dias_restantes = max(0, (h.ciclo_estimado or 0) - passados)
            except:
                h.atrasada = False; h.dias_restantes = 0

    historico = Hortalica.query.filter_by(fazenda_id=id, status='Colhido').all()
    if len(historico) >= 2:
        tipos_ativos = set([h.nome for h in fazenda.hortalicas if h.status != 'Colhido'])
        for tipo in tipos_ativos:
            dados_tipo = [h for h in historico if h.nome == tipo and h.data_plantio and h.data_colheita]
            if len(dados_tipo) >= 2:
                try:
                    X = np.array(range(len(dados_tipo))).reshape(-1, 1)
                    Y = []
                    for h in dados_tipo:
                        d_p = datetime.strptime(h.data_plantio, '%Y-%m-%d').date()
                        d_c = datetime.strptime(h.data_colheita, '%Y-%m-%d').date()
                        Y.append((d_c - d_p).days)
                    model = LinearRegression().fit(X, Y)
                    pred = model.predict([[len(dados_tipo)]])
                    previsoes_ia[tipo] = round(float(pred[0]), 1)
                except: continue

    if PLANTA_FOCO_ID:
        reg_simulador = RegistroHidrico.query.filter_by(fazenda_id=id, origem="simulador", hortalica_id=PLANTA_FOCO_ID).order_by(RegistroHidrico.id.desc()).limit(15).all()
        reg_sensor = RegistroHidrico.query.filter_by(fazenda_id=id, origem="sensor", hortalica_id=PLANTA_FOCO_ID).order_by(RegistroHidrico.id.desc()).limit(15).all()
        todos_recentes = RegistroHidrico.query.filter_by(fazenda_id=id, hortalica_id=PLANTA_FOCO_ID).order_by(RegistroHidrico.id.desc()).limit(15).all()
    else:
        reg_simulador = []
        reg_sensor = []
        todos_recentes = []

    reg_simulador.reverse()
    labels_simulador = [r.data_leitura for r in reg_simulador]
    dados_simulador = [r.nivel_porcentagem for r in reg_simulador]

    reg_sensor.reverse()
    labels_sensor = [r.data_leitura for r in reg_sensor]
    dados_sensor = [r.nivel_porcentagem for r in reg_sensor]

    if todos_recentes:
        stats['media_h2o'] = round(sum(r.nivel_porcentagem for r in todos_recentes) / len(todos_recentes), 1)
        media_val = stats['media_h2o']
        
        # Descobre a categoria da planta em foco para ajustar os limites da IA
        categoria_foco = "hortalica"
        nome_foco_str = "Planta Monitorada"
        if PLANTA_FOCO_ID:
            p_foco = db.session.get(Hortalica, PLANTA_FOCO_ID)
            if p_foco:
                categoria_foco = p_foco.categoria_hidrica or "hortalica"
                nome_foco_str = p_foco.nome
        
        # Define os limites com base na categoria da planta em foco
        if categoria_foco == 'arida':
            if media_val < 5:
                stats['insight_h2o'] = {"tipo": "perigo", "msg": f"{nome_foco_str} (Árida): Nível muito baixo ({media_val}%). Considere uma rega ligeira."}
            elif media_val > 40:
                stats['insight_h2o'] = {"tipo": "alerta", "msg": f"{nome_foco_str} (Árida): Nível elevado ({media_val}%). Risco de apodrecimento das raízes, reduza a rega."}
            else:
                stats['insight_h2o'] = {"tipo": "sucesso", "msg": f"{nome_foco_str} (Árida): Nível hídrico perfeito ({media_val}%). Condições ideais para suculentas/cactos."}
                
        elif categoria_foco == 'tropical':
            if media_val < 50:
                stats['insight_h2o'] = {"tipo": "perigo", "msg": f"{nome_foco_str} (Tropical): Nível baixo ({media_val}%). Aumente a irrigação urgentemente."}
            elif media_val > 90:
                stats['insight_h2o'] = {"tipo": "alerta", "msg": f"{nome_foco_str} (Tropical): Nível muito alto ({media_val}%). Solo demasiado encharcado."}
            else:
                stats['insight_h2o'] = {"tipo": "sucesso", "msg": f"{nome_foco_str} (Tropical): Nível hídrico ideal ({media_val}%). Mantenha o fluxo."}
                
        else: # Hortaliças Comuns (Padrão)
            if media_val < 30.0:
                stats['insight_h2o'] = {"tipo": "perigo", "msg": f"{nome_foco_str}: Nível baixo ({media_val}%). Aumente a irrigação para evitar o estresse hídrico."}
            elif media_val > 70.0:
                stats['insight_h2o'] = {"tipo": "alerta", "msg": f"{nome_foco_str}: Nível elevado ({media_val}%). Reduza a irrigação para evitar saturação."}
            else:
                stats['insight_h2o'] = {"tipo": "sucesso", "msg": f"{nome_foco_str}: Nível hídrico ideal ({media_val}%). Mantenha o ciclo atual."}

    stats['total_ativas'] = qtd_ativas
    stats['tempo_medio'] = round(total_ciclos / qtd_ativas, 1) if qtd_ativas > 0 else 0
    stats['previsoes'] = previsoes_ia

    if filtro == 'Crescendo': hortalicas_exibidas = [h for h in fazenda.hortalicas if h.status != 'Colhido']
    elif filtro == 'Colhido': hortalicas_exibidas = [h for h in fazenda.hortalicas if h.status == 'Colhido']
    else: hortalicas_exibidas = fazenda.hortalicas

    return render_template('index.html', fazenda=fazenda, hortalicas=hortalicas_exibidas, 
                           stats=stats, chart_data=contagem_variedades, 
                           labels_simulador=labels_simulador, dados_simulador=dados_simulador,
                           labels_sensor=labels_sensor, dados_sensor=dados_sensor, hoje=hoje,
                           planta_foco_id=PLANTA_FOCO_ID)

# --- OPERAÇÕES DE CRUD E API ---

@app.route('/add_hortalica/<int:fazenda_id>', methods=['POST'])
@login_required
def add_hortalica(fazenda_id):
    nome = request.form.get('nome')
    data = request.form.get('data_plantio')
    ciclo = request.form.get('ciclo_estimado')
    categoria = request.form.get('categoria_hidrica', 'hortalica')
    
    if nome and data:
        nova_hortalica = Hortalica(
            nome=nome, 
            data_plantio=data, 
            ciclo_estimado=int(ciclo or 0), 
            fazenda_id=fazenda_id,
            categoria_hidrica=categoria
        )
        db.session.add(nova_hortalica)
        db.session.commit()
    return redirect(url_for('ver_fazenda', id=fazenda_id))

# --- ROTA PARA EDITAR HORTALIÇA ---
@app.route('/editar_hortalica/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_hortalica(id):
    h = db.session.get(Hortalica, id)
    if not h or h.fazenda.usuario_id != current_user.id:
        return "Acesso Negado", 403
        
    if request.method == 'POST':
        h.nome = request.form.get('nome')
        h.data_plantio = request.form.get('data_plantio')
        ciclo = request.form.get('ciclo_estimado')
        h.ciclo_estimado = int(ciclo) if ciclo else 0
        h.categoria_hidrica = request.form.get('categoria_hidrica', 'hortalica')
        db.session.commit()
        return redirect(url_for('ver_fazenda', id=h.fazenda_id))
        
    return render_template('editar_hortalica.html', hortalica=h)

@app.route('/colher/<int:id>/<int:fazenda_id>', methods=['POST'])
@login_required
def colher(id, fazenda_id):
    h = db.session.get(Hortalica, id)
    if h:
        data_f = request.form.get('data_colheita')
        h.data_colheita = data_f if data_f else datetime.now().strftime('%Y-%m-%d')
        h.status = "Colhido"
        db.session.commit()
    return redirect(url_for('ver_fazenda', id=fazenda_id))

@app.route('/deletar/<int:id>/<int:fazenda_id>')
@login_required
def deletar(id, fazenda_id):
    h = db.session.get(Hortalica, id)
    if h:
        db.session.delete(h); db.session.commit()
    return redirect(url_for('ver_fazenda', id=fazenda_id))

@app.route('/exportar_csv/<int:fazenda_id>')
@login_required
def exportar_csv(fazenda_id):
    fazenda = db.session.get(Fazenda, fazenda_id)
    if not fazenda: return "Not Found", 404
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Hortalica', 'Data Plantio', 'Data Colheita', 'Status', 'Ciclo Estimado', 'Categoria Hidrica'])
    for h in fazenda.hortalicas:
        cw.writerow([h.nome, h.data_plantio, h.data_colheita, h.status, h.ciclo_estimado, h.categoria_hidrica])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=relatorio_{fazenda.nome}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# --- ENDPOINTS DA PLANTA EM FOCO ---
@app.route('/api/focar_planta/<int:hortalica_id>', methods=['POST'])
@login_required
def focar_planta(hortalica_id):
    global PLANTA_FOCO_ID

    planta = db.session.get(Hortalica, hortalica_id)

    if not planta:
        return jsonify({"erro": "Planta não encontrada"}), 404

    # Se já está monitorando esta planta, desativa o monitoramento
    if PLANTA_FOCO_ID == hortalica_id:
        PLANTA_FOCO_ID = None
        return jsonify({
            "status": "desativado",
            "nome": planta.nome,
            "id": hortalica_id
        })

    # Caso contrário, começa a monitorar esta planta
    PLANTA_FOCO_ID = hortalica_id

    return jsonify({
        "status": "sucesso",
        "nome": planta.nome,
        "id": hortalica_id
    })

# --- ENDPOINTS DO SENSOR FÍSICO (USB) ---
@app.route('/api/sensor_fisico/toggle', methods=['POST'])
@login_required
def toggle_sensor_fisico():
    global sensor_fisico_ativo
    if sensor_fisico_ativo:
        sensor_fisico_ativo = False
        return jsonify({"status": "desativado", "mensagem": "Recebimento de dados do vaso pausado."})
    else:
        sensor_fisico_ativo = True
        return jsonify({"status": "ativo", "mensagem": "Recebimento de dados do vaso ativado."})

@app.route('/api/sensor_fisico/status', methods=['GET'])
@login_required
def status_sensor_fisico():
    return jsonify({"ativo": sensor_fisico_ativo})

# --- ENDPOINTS DE ATUALIZAÇÃO DINÂMICA (AJAX) ---
@app.route('/api/dados_grafico/<int:fazenda_id>', methods=['GET'])
@login_required
def dados_grafico(fazenda_id):
    global PLANTA_FOCO_ID

    if PLANTA_FOCO_ID:
        reg_sensor = RegistroHidrico.query.filter_by(
            fazenda_id=fazenda_id,
            origem="sensor",
            hortalica_id=PLANTA_FOCO_ID
        ).order_by(RegistroHidrico.id.desc()).limit(15).all()
    else:
        reg_sensor = []

    reg_sensor.reverse()
    labels_sensor = [r.data_leitura for r in reg_sensor]
    dados_sensor = [r.nivel_porcentagem for r in reg_sensor]

    if PLANTA_FOCO_ID:
        reg_simulador = RegistroHidrico.query.filter_by(
            fazenda_id=fazenda_id,
            origem="simulador",
            hortalica_id=PLANTA_FOCO_ID
        ).order_by(RegistroHidrico.id.desc()).limit(15).all()
    else:
        reg_simulador = []

    reg_simulador.reverse()
    labels_simulador = [r.data_leitura for r in reg_simulador]
    dados_simulador = [r.nivel_porcentagem for r in reg_simulador]

    fazenda = db.session.get(Fazenda, fazenda_id)
    umidades_plantas = {}

    if fazenda:
        for h in fazenda.hortalicas:
            umidades_plantas[h.id] = h.umidade_atual or 0.0

    return jsonify({
        "labels_sensor": labels_sensor,
        "dados_sensor": dados_sensor,
        "labels_simulador": labels_simulador,
        "dados_simulador": dados_simulador,
        "umidades_plantas": umidades_plantas
    })

# --- ENDPOINTS DO SIMULADOR INTEGRADO ---
@app.route('/api/simulador/toggle/<int:fazenda_id>', methods=['POST'])
@login_required
def toggle_simulador(fazenda_id):
    global simulador_ativo, simulador_thread
    if simulador_ativo:
        simulador_ativo = False
        return jsonify({"status": "desativado", "mensagem": "Simulador pausado com sucesso."})
    else:
        simulador_ativo = True
        simulador_thread = threading.Thread(target=rodar_simulacao, args=(fazenda_id,), daemon=True)
        simulador_thread.start()
        return jsonify({"status": "ativo", "mensagem": "Simulador iniciado em segundo plano."})

@app.route('/api/simulador/status', methods=['GET'])
@login_required
def status_simulador():
    return jsonify({"ativo": simulador_ativo})

if __name__ == '__main__':
    app.run(debug=True, port=8080, use_reloader=False)