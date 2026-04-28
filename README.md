# 🌿 BioUrban - Sistema Inteligente de Monitoramento Hídrico

O **BioUrban** é uma plataforma de gestão para fazendas urbanas e unidades de cultivo inteligente desenvolvida para monitoramento hídrico eficiente. O projeto integra monitoramento em tempo real via sensores IoT, análise de ciclo de cultivo e ferramentas de exportação de dados para otimizar a produtividade agrícola urbana.

## 🚀 Funcionalidades

- **Dashboard de Gestão:** Visualização consolidada de unidades ativas, métricas de cultivo e tempo médio.
- **Monitoramento IoT:** Gráficos de consumo hídrico em tempo real alimentados via API.
- **Gestão de Lotes:** Controle de plantio com indicadores de status (Crescendo/Colhido) e alertas visuais de atraso.
- **Análise Visual:** Gráficos interativos (Chart.js) para distribuição de variedades e histórico de consumo.
- **Relatórios:** Exportação do histórico completo de cultivos em formato CSV para análise externa.
- **Segurança:** Sistema de autenticação de usuários para isolamento de dados por perfil.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Framework Web:** Flask
- **Banco de Dados:** SQLite (SQLAlchemy)
- **Frontend:** HTML5, CSS3 (Flexbox/Grid), JavaScript, Chart.js
- **Simulação IoT:** Script Python (Requests)

## 🔧 Instalação e Execução

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU_USUARIO/biourbanteste.git](https://github.com/SEU_USUARIO/biourbanteste.git)
   cd biourban-main
Crie e ative o ambiente virtual:

Bash
python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
Instale as dependências:

Bash
pip install flask flask-sqlalchemy flask-login requests
Inicie o servidor:

Bash
python app.py
Acesse no navegador: http://127.0.0.1:8080

📡 Simulação de Sensores (IoT)
Para validar o funcionamento dos gráficos de consumo:

Com o servidor app.py rodando, abra um novo terminal.

Execute o simulador:

Bash
python simulador_iot.py
Insira o ID da Fazenda (presente na URL do dashboard) para iniciar o fluxo de dados.

📂 Estrutura de Arquivos
app.py: Servidor principal e rotas da aplicação.

models.py: Definição das classes e esquema do banco de dados.

simulador_iot.py: Script para simular o envio de dados de sensores.

templates/: Arquivos de interface (Jinja2).

static/: Estilização e recursos visuais.

✒️ Autores
Julio Cesar - Desenvolvedor e Estudante de Ciência da Computação.
Henrique Barros - Desenvolvedor e Estudante de Ciência da Computação.
Igor Matos - Desenvolvedor e Estudante de Ciência da Computação.