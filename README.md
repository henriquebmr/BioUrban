# 🌿 BioUrban — Sistema Inteligente de Monitoramento Hídrico

O **BioUrban** é uma plataforma de gestão e monitoramento para fazendas urbanas e unidades de cultivo inteligente.

O sistema permite acompanhar o desenvolvimento das plantas, registrar lotes de cultivo e monitorar a umidade do solo por meio de sensores físicos ou dados simulados.

O projeto integra **Python, Flask, SQLite, ESP32 e sensores IoT**, disponibilizando os dados em um dashboard web.

---

## 🚀 Funcionalidades

- 📊 Dashboard para acompanhamento das plantações;
- 🌱 Cadastro e gerenciamento de plantas e lotes;
- 💧 Monitoramento da umidade do solo;
- 📡 Integração física com ESP32;
- 🔌 Comunicação do ESP32 com o computador via USB/Serial;
- 🧪 Simulador IoT para testes sem o hardware físico;
- 📈 Gráficos de monitoramento em tempo real;
- 🎯 Seleção de uma planta para monitoramento individual;
- 🔄 Ativação e desativação do sensor físico;
- 📋 Recomendações de acordo com a necessidade hídrica da planta;
- 🔐 Sistema de autenticação de usuários;
- 📄 Exportação de dados para análise.

---

## 🧠 Arquitetura do sistema

### Sensor físico

```text
Sensor capacitivo
       ↓
     ESP32
       ↓
   USB / Serial
       ↓
     Python
       ↓
     Flask
       ↓
    SQLite
       ↓
   Dashboard
```

### Simulador

```text
Simulador IoT
       ↓
     Flask
       ↓
    SQLite
       ↓
   Dashboard
```

O simulador e o sensor físico são independentes. Dessa forma, o sistema pode ser executado mesmo sem o ESP32 conectado.

---

## 📡 Integração com o ESP32

O BioUrban possui integração física com um **ESP32**, conectado ao computador através de um cabo USB.

O ESP32 recebe os dados de um **sensor capacitivo de umidade do solo** e envia as informações para o sistema através da comunicação serial.

### Componentes utilizados

- ESP32 ESP-WROOM-32;
- Sensor capacitivo de umidade do solo;
- Display OLED 0.96" I2C;
- Protoboard;
- Cabos jumper;
- Cabo USB.

### Comunicação

A comunicação atual utiliza:

```text
ESP32 → USB → Porta Serial → Python
```

A aplicação Python utiliza a biblioteca **PySerial** para receber os dados enviados pelo ESP32.

A configuração utilizada no projeto é:

```text
Porta: COM3
Baud rate: 9600
```

---

## 🌱 Calibração do sensor

O sensor capacitivo foi calibrado experimentalmente utilizando diferentes condições de umidade do solo.

| Condição | Valor aproximado |
|---|---:|
| Terra seca | 3115 |
| Terra úmida | 2415 |
| Terra muito úmida | 1144 |

A partir desses valores, o ESP32 converte a leitura analógica em uma porcentagem de umidade de **0% a 100%**.

### Classificação utilizada

| Umidade | Status |
|---|---|
| Menor que 30% | SECO |
| 30% a 69% | ADEQUADO |
| 70% ou mais | MUITO ÚMIDO |

> A porcentagem representa uma escala experimental de calibração utilizada no projeto e não deve ser interpretada como uma medida universal de umidade volumétrica do solo.

---

## 🖥️ Tecnologias utilizadas

### Backend

- Python 3
- Flask
- SQLAlchemy
- Flask-Login
- SQLite
- PySerial

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2
- Chart.js
- Font Awesome

### Hardware

- ESP32
- Sensor capacitivo de umidade do solo
- Display OLED SSD1306

---

## 🔧 Instalação e execução

### 1. Clonar o repositório

```bash
git clone https://github.com/henriquebmr/BioUrban.git
```

Entrar na pasta:

```bash
cd BioUrban
```

### 2. Criar o ambiente virtual

No Windows:

```bash
python -m venv venv
```

Ativar:

```bash
venv\Scripts\activate
```

No Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install flask flask-sqlalchemy flask-login requests numpy scipy scikit-learn pyserial
```

### 4. Executar o sistema

```bash
python app.py
```

Após iniciar o servidor, acessar:

```text
http://127.0.0.1:8080
```

---

## 🧪 Simulador IoT

O projeto possui um simulador para permitir testes mesmo sem o ESP32 conectado.

O simulador pode gerar leituras de umidade e enviar os dados para o banco de dados da aplicação.

Também existe a possibilidade de utilizar o simulador diretamente pelo sistema através do controle disponível no dashboard.

O arquivo responsável pela simulação independente é:

```text
simulador_iot.py
```

Para executar o simulador independente:

```bash
python simulador_iot.py
```

---

## 📊 Monitoramento em tempo real

O dashboard apresenta gráficos com as leituras recebidas pelo sistema.

É possível monitorar uma planta específica através da opção:

```text
Monitorar Planta
```

Ao selecionar uma planta, o sistema passa a apresentar os dados relacionados àquela planta nos gráficos de monitoramento.

O monitoramento pode ser desativado através do mesmo botão.

---

## 🔌 Controle do sensor físico

O sensor físico possui um controle independente dentro do sistema.

O sensor inicia **desativado** quando a aplicação é aberta.

Quando ativado, o sistema passa a receber os dados enviados pelo ESP32 através da porta serial configurada.

Isso permite utilizar o sistema com ou sem o hardware conectado.

---

## 📁 Estrutura do projeto

```text
BioUrban/
│
├── app.py
├── models.py
├── simulador_iot.py
├── README.md
│
├── instance/
│   └── biourban_pro.db
│
├── templates/
│   ├── dashboard.html
│   ├── editar_hortalica.html
│   ├── index.html
│   ├── layout.html
│   ├── login.html
│   └── register.html
│
├── static/
│   └── images/
│
└── .vscode/
```

### Principais arquivos

**`app.py`**  
Servidor Flask, rotas da aplicação, integração com o ESP32, simulador e APIs.

**`models.py`**  
Modelos do banco de dados e estruturas utilizadas pelo sistema.

**`simulador_iot.py`**  
Simulador responsável por gerar dados para testes do monitoramento.

**`templates/`**  
Interfaces HTML da aplicação utilizando Jinja2.

**`static/`**  
Arquivos estáticos, imagens e recursos visuais.

**`instance/biourban_pro.db`**  
Banco de dados SQLite utilizado pela aplicação.

---

## 👨‍💻 Autores

**Julio Cesar**  
Desenvolvedor e estudante de Ciência da Computação.

**Henrique Barros**  
Desenvolvedor e estudante de Ciência da Computação.

**Igor Matos**  
Desenvolvedor e estudante de Ciência da Computação.

---

## 🎓 Projeto acadêmico

Projeto desenvolvido como parte do **Trabalho de Conclusão de Curso (TCC)** em Ciência da Computação.

**BioUrban — Sistema Inteligente de Monitoramento Hídrico.**
