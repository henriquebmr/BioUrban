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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biourban_pro.db'
app.config['SECRET_KEY'] = 'chave-segura-biourban-2026'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# --- CONTROLE GLOBAL DO SIMULADOR IOT EM SEGUNDO PLANO ---
simulador_ativo = False
simulador_thread = None

# Calibração real do sensor ESP32
ADC_NO_AR = 3180
ADC_NA_AGUA = 1150

def rodar_simulacao(fazenda_id):
    global simulador_ativo
    while simulador_ativo:
        # Gera leitura analógica simulada entre Terra Seca (2945) e Terra Muito Úmida (1400)
        adc_simulado = random.randint(1400, 2945)
        pct = (ADC_NO_AR - adc_simulado) / (ADC_NO_AR - ADC_NA_AGUA) * 100.0
        porcentagem = round(max(0.0, min(100.0, pct)), 1)

        with app.app_context():
            novo = RegistroHidrico(
                nivel_porcentagem=porcentagem,
                data_leitura=datetime.now().strftime('%H:%M:%S'),
                origem="simulador",
                fazenda_id=fazenda_id
            )
            db.session.add(novo)
            db.session.commit()

        # Configurado para enviar a cada 60 segundos (1 minuto)
        time.sleep(60)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

with app.app_context():
    db.create_all()

# Filtro para calcular dias de cultivo no HTML
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
    fazenda = Fazenda.query.get_or_404(id)
    if fazenda.usuario_id != current_user.id: return "Acesso Negado", 403
    
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

    # 1. PROCESSAMENTO DE LOTES
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

    # 2. IA PREDITIVA (COLHEITA)
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

    # 3. PROCESSAMENTO HÍDRICO SEPARADO POR ORIGEM (SIMULADOR vs SENSOR)
    reg_simulador = RegistroHidrico.query.filter_by(fazenda_id=id, origem="simulador").order_by(RegistroHidrico.id.desc()).limit(15).all()
    reg_simulador.reverse()
    labels_simulador = [r.data_leitura for r in reg_simulador]
    dados_simulador = [r.nivel_porcentagem for r in reg_simulador]

    reg_sensor = RegistroHidrico.query.filter_by(fazenda_id=id, origem="sensor").order_by(RegistroHidrico.id.desc()).limit(15).all()
    reg_sensor.reverse()
    labels_sensor = [r.data_leitura for r in reg_sensor]
    dados_sensor = [r.nivel_porcentagem for r in reg_sensor]

    todos_recentes = RegistroHidrico.query.filter_by(fazenda_id=id).order_by(RegistroHidrico.id.desc()).limit(15).all()
    if todos_recentes:
        stats['media_h2o'] = round(sum(r.nivel_porcentagem for r in todos_recentes) / len(todos_recentes), 1)
        if stats['media_h2o'] < 30.0:
            stats['insight_h2o'] = {"tipo": "perigo", "msg": f"Nível baixo ({stats['media_h2o']}%). Aumente a irrigação para evitar o estresse hídrico das raízes."}
        elif stats['media_h2o'] > 80.0:
            stats['insight_h2o'] = {"tipo": "alerta", "msg": f"Nível elevado ({stats['media_h2o']}%). Reduza a irrigação para evitar saturação."}
        else:
            stats['insight_h2o'] = {"tipo": "sucesso", "msg": f"Nível hídrico ideal ({stats['media_h2o']}%). Mantenha o ciclo de irrigação atual."}

    stats['total_ativas'] = qtd_ativas
    stats['tempo_medio'] = round(total_ciclos / qtd_ativas, 1) if qtd_ativas > 0 else 0
    stats['previsoes'] = previsoes_ia

    if filtro == 'Crescendo': hortalicas_exibidas = [h for h in fazenda.hortalicas if h.status != 'Colhido']
    elif filtro == 'Colhido': hortalicas_exibidas = [h for h in fazenda.hortalicas if h.status == 'Colhido']
    else: hortalicas_exibidas = fazenda.hortalicas

    return render_template('index.html', fazenda=fazenda, hortalicas=hortalicas_exibidas, 
                           stats=stats, chart_data=contagem_variedades, 
                           labels_simulador=labels_simulador, dados_simulador=dados_simulador,
                           labels_sensor=labels_sensor, dados_sensor=dados_sensor, hoje=hoje)

# --- OPERAÇÕES DE CRUD E API ---

@app.route('/add_hortalica/<int:fazenda_id>', methods=['POST'])
@login_required
def add_hortalica(fazenda_id):
    nome = request.form.get('nome')
    data = request.form.get('data_plantio')
    ciclo = request.form.get('ciclo_estimado')
    if nome and data:
        db.session.add(Hortalica(nome=nome, data_plantio=data, ciclo_estimado=int(ciclo or 0), fazenda_id=fazenda_id))
        db.session.commit()
    return redirect(url_for('ver_fazenda', id=fazenda_id))

@app.route('/colher/<int:id>/<int:fazenda_id>', methods=['POST'])
@login_required
def colher(id, fazenda_id):
    h = Hortalica.query.get(id)
    if h:
        data_f = request.form.get('data_colheita')
        h.data_colheita = data_f if data_f else datetime.now().strftime('%Y-%m-%d')
        h.status = "Colhido"
        db.session.commit()
    return redirect(url_for('ver_fazenda', id=fazenda_id))

@app.route('/deletar/<int:id>/<int:fazenda_id>')
@login_required
def deletar(id, fazenda_id):
    h = Hortalica.query.get(id)
    if h:
        db.session.delete(h); db.session.commit()
    return redirect(url_for('ver_fazenda', id=fazenda_id))

@app.route('/exportar_csv/<int:fazenda_id>')
@login_required
def exportar_csv(fazenda_id):
    fazenda = Fazenda.query.get_or_404(fazenda_id)
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Hortalica', 'Data Plantio', 'Data Colheita', 'Status', 'Ciclo Estimado'])
    for h in fazenda.hortalicas:
        cw.writerow([h.nome, h.data_plantio, h.data_colheita, h.status, h.ciclo_estimado])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=relatorio_{fazenda.nome}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/api/sensor_hidrico', methods=['POST'])
def receber_dados_sensor():
    data = request.get_json()

    if data:
        # Novo padrão: umidade
        # Mantém compatibilidade temporária com o padrão antigo: consumo
        umidade = data.get('umidade')

        if umidade is None:
            umidade = data.get('consumo')

        if umidade is None:
            return jsonify({
                "erro": "Campo 'umidade' não informado"
            }), 400

        novo = RegistroHidrico(
            nivel_porcentagem=float(umidade),
            data_leitura=datetime.now().strftime('%H:%M:%S'),
            origem="sensor",
            fazenda_id=data['fazenda_id']
        )

        db.session.add(novo)
        db.session.commit()

        return jsonify({
            "status": "sucesso",
            "umidade": float(umidade)
        }), 201

    return jsonify({"erro": "falha"}), 400

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
    app.run(debug=True, port=8080)