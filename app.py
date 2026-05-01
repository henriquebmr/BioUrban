from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, Usuario, Fazenda, Hortalica, RegistroHidrico
from datetime import datetime
import csv
import io
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biourban_pro.db'
app.config['SECRET_KEY'] = 'chave-segura-biourban-2026'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

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

    # --- INICIALIZAÇÃO DO DICIONÁRIO STATS (CORREÇÃO DO ERRO) ---
    stats = {
        'total_ativas': 0,
        'tempo_medio': 0,
        'total_h2o': 0,
        'media_h2o': 0,
        'filtro_atual': filtro,
        'previsoes': {},
        'insight_h2o': None
    }

    # 1. PROCESSAMENTO DE LOTES (Cálculo de dias e atrasos)
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

    # 2. IA PREDITIVA (COLHEITA) - Baseada em Histórico
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

    # 3. PROCESSAMENTO HÍDRICO EXPANDIDO (IoT)
    registros = RegistroHidrico.query.filter_by(fazenda_id=id).order_by(RegistroHidrico.id.desc()).limit(15).all()
    if registros:
        soma_h2o = sum(r.consumo_litros for r in registros)
        stats['total_h2o'] = round(soma_h2o, 2)
        stats['media_h2o'] = round(soma_h2o / len(registros), 2)
        
        # IA Prescritiva BioUrban (Thresholds 1L e 2L)
        if stats['media_h2o'] >= 2.0:
            stats['insight_h2o'] = {"tipo": "perigo", "msg": f"Consumo elevado ({stats['media_h2o']}L). Reduza o fluxo para evitar desperdício."}
        elif stats['media_h2o'] <= 1.0:
            stats['insight_h2o'] = {"tipo": "alerta", "msg": f"Consumo baixo ({stats['media_h2o']}L). Aumente a irrigação para hidratação das raízes."}
        else:
            stats['insight_h2o'] = {"tipo": "sucesso", "msg": f"Nível ideal ({stats['media_h2o']}L). Mantenha o fluxo atual."}

    # Atualizando métricas finais no stats
    stats['total_ativas'] = qtd_ativas
    stats['tempo_medio'] = round(total_ciclos / qtd_ativas, 1) if qtd_ativas > 0 else 0
    stats['previsoes'] = previsoes_ia

    # Dados para Gráficos
    registros_grafico = list(registros)
    registros_grafico.reverse()
    labels_h2o = [r.data_leitura[8:10]+"/"+r.data_leitura[5:7] for r in registros_grafico]
    dados_h2o = [r.consumo_litros for r in registros_grafico]

    # Filtro da Tabela
    if filtro == 'Crescendo': hortalicas_exibidas = [h for h in fazenda.hortalicas if h.status != 'Colhido']
    elif filtro == 'Colhido': hortalicas_exibidas = [h for h in fazenda.hortalicas if h.status == 'Colhido']
    else: hortalicas_exibidas = fazenda.hortalicas

    return render_template('index.html', fazenda=fazenda, hortalicas=hortalicas_exibidas, 
                           stats=stats, chart_data=contagem_variedades, 
                           labels_h2o=labels_h2o, dados_h2o=dados_h2o, hoje=hoje)

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
        novo = RegistroHidrico(consumo_litros=data['consumo'], 
                               data_leitura=datetime.now().strftime('%Y-%m-%d'), 
                               fazenda_id=data['fazenda_id'])
        db.session.add(novo); db.session.commit()
        return jsonify({"status": "sucesso"}), 201
    return jsonify({"erro": "falha"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8080)