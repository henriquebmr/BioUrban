# 🌿 BioUrban Pro - Sistema Inteligente de Monitoramento Agrícola e Gestão Hídrica IoT

O **BioUrban Pro** é uma plataforma web desenvolvida para monitoramento e gestão inteligente de fazendas urbanas e sistemas hidropônicos. O projeto combina **IoT (Internet das Coisas)** com **Inteligência Artificial Preditiva e Prescritiva** para otimizar o uso da água e prever prazos de colheita.

---

## 🚀 Tecnologias Utilizadas

- **Backend:** Python (Flask, Flask-SQLAlchemy, Flask-Login)
- **Data Science & ML:** NumPy, SciPy, Scikit-learn (Regressão Linear)
- **Frontend:** HTML5, CSS3, JavaScript, Chart.js, FontAwesome
- **Banco de Dados:** SQLite
- **IoT & Hardware:** ESP32, Sensor Capacitivo de Umidade do Solo, Display OLED SSD1306

---

## 🛠️ Passo a Passo para Instalação e Execução

Siga o roteiro de comandos abaixo no terminal para verificar seu ambiente, instalar as dependências necessárias e rodar a aplicação no seu computador.

### 1. Verificação do Ambiente Python e Pip

Certifique-se de que o Python e o gerenciador de pacotes `pip` estão instalados corretamente:

```bash
python --version
python -m pip --version
2. Instalação das Dependências
Instale as bibliotecas necessárias para a aplicação web, comunicação HTTP e modelos de aprendizado de máquina:

Bash
python -m pip install flask flask-sqlalchemy flask-login requests numpy scipy scikit-learn
3. Validação do Ambiente Científico
Verifique se os módulos de ciência de dados foram instalados e estão funcionais:

Bash
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import scipy; print('SciPy:', scipy.__version__)"
python -c "import sklearn; print('Scikit-learn:', sklearn.__version__)"
python -c "import numpy; import scipy; from sklearn.linear_model import LinearRegression; print('OK - ambiente científico funcionando')"
4. Execução da Aplicação
Inicie o servidor local da aplicação Flask:

Bash
python app.py
Após executar o comando, o servidor estará ativo no seu navegador em: http://127.0.0.1:8080

📡 Simulação e Integração IoT (ESP32)
Simulador Virtual (Dashboard): Você pode ativar o simulador em segundo plano diretamente pela interface do painel clicando no botão Simulador: OFF/ON.

Sensor Físico ESP32: Ao conectar o microcontrolador ESP32 na mesma rede Wi-Fi, as leituras analógicas calibradas (0% a 100%) serão transmitidas via HTTP POST para a rota /api/sensor_hidrico e exibidas no gráfico do Sensor Físico.
