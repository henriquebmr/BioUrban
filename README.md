# 🌿 BioUrban Pro - Sistema Inteligente de Monitoramento Agrícola e Gestão Hídrica IoT

O **BioUrban Pro** é uma plataforma web desenvolvida para monitoramento e gestão inteligente de fazendas urbanas e sistemas de cultivo. O projeto combina recursos de **IoT (Internet das Coisas)**, processamento de dados e funcionalidades de **Inteligência Artificial** para auxiliar no acompanhamento das condições de cultivo, gerenciamento de lotes e análise das informações coletadas.

O sistema possui integração com **ESP32 e sensor capacitivo de umidade**, além de um **simulador IoT** que permite realizar testes sem a necessidade do hardware físico.

---

## 🚀 Principais Funcionalidades

### 📡 Monitoramento IoT Dual

O sistema possui duas fontes de dados para o monitoramento:

- **Sensor físico:** ESP32 conectado ao computador através de USB/Serial, utilizando a porta `COM3`.
- **Simulador virtual:** geração de leituras simuladas para testes e validação do sistema.

As duas fontes utilizam uma escala de umidade de **0% a 100%** e são identificadas no sistema de acordo com sua origem.

### 💧 Monitoramento de Umidade

O sensor capacitivo realiza a leitura analógica do ambiente de cultivo através do ESP32.

As leituras são convertidas para uma escala percentual de umidade utilizando uma calibração experimental:

| Condição | Valor ADC | Umidade |
|---|---:|---:|
| Terra seca | 3115 | 0% |
| Terra úmida | 2415 | 50% |
| Terra muito úmida | 1144 | 100% |

A conversão utiliza interpolação entre esses pontos e limita os resultados ao intervalo de **0% a 100%**.

> **Observação:** os valores representam uma calibração experimental realizada com o sensor utilizado no projeto. A porcentagem representa uma escala relativa de umidade para o sistema e não uma medição universal de umidade volumétrica do solo.

### 🖥️ Monitoramento pelo Dashboard

O painel apresenta as informações coletadas pelo sistema através de gráficos e indicadores, permitindo acompanhar:

- média recente de umidade;
- leituras do sensor físico;
- leituras do simulador;
- informações dos lotes;
- condições de cultivo;
- recomendações apresentadas pelo sistema.

### 🌱 Categorias Hídricas

O sistema possui categorias de cultivo e parâmetros relacionados às necessidades de umidade, permitindo utilizar diferentes referências para o acompanhamento das plantas.

Entre as categorias utilizadas estão:

- **Hortaliças Comuns**
- **Cactos e Suculentas**
- **Plantas Tropicais**

### 🤖 IA Prescritiva

O sistema possui um card de orientação integrado ao dashboard, utilizado para apresentar recomendações relacionadas às condições observadas no cultivo.

### 📈 Predição de Colheita

O sistema utiliza recursos de análise de dados e **Regressão Linear**, através do `scikit-learn` e `NumPy`, para auxiliar na estimativa de prazos relacionados ao cultivo.

### 🌾 Gestão de Lotes

O sistema permite realizar operações relacionadas aos lotes de cultivo, incluindo:

- cadastro de lotes;
- registro de espécie;
- definição de data de plantio;
- definição de ciclo estimado;
- acompanhamento do cultivo;
- registro de colheita;
- exportação de dados em CSV.

---

## 🧰 Tecnologias Utilizadas

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login

### Data Science e Machine Learning

- NumPy
- SciPy
- Scikit-learn
- Regressão Linear

### Frontend

- HTML5
- CSS3
- JavaScript
- AJAX
- Chart.js
- FontAwesome

### Banco de Dados

- SQLite

### IoT e Hardware

- ESP32
- Sensor capacitivo de umidade
- Display OLED I2C
- Comunicação USB/Serial
- PySerial

---

# 🔌 Integração com o ESP32

O BioUrban possui integração física com um ESP32 conectado ao computador através de um cabo USB.

A comunicação atual utiliza a porta serial do computador.

### Fluxo da comunicação

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

🛠️ Instalação e Execução
Esta seção apresenta o procedimento completo para configurar o ambiente, instalar as dependências e executar o BioUrban.
📋 1. Pré-requisitos
Antes de iniciar, certifique-se de possuir:
- 🐍 Python instalado;
- 📦 pip instalado;
- 🛠️ Arduino IDE instalada, caso utilize o ESP32 físico;
- 🔌 ESP32 configurado na Arduino IDE, caso utilize o sensor físico;
- 🔗 Cabo USB para conectar o ESP32 ao computador.
O uso do ESP32 é opcional para executar a aplicação, pois o projeto possui um simulador IoT.

📥 2. Clonar o Repositório
Caso ainda não tenha o projeto no computador, clone o repositório:
git clone https://github.com/djuliocesar2/biourbanteste.git

Depois, entre na pasta do projeto:
cd biourbanteste

🐍 3. Verificar o Python e o Pip
Verifique se o Python está instalado corretamente:
python --version

Depois, verifique o pip:
python -m pip --version

Se os comandos retornarem as versões instaladas, o ambiente está pronto para continuar.

📦 4. Instalar as Dependências
Instale as bibliotecas utilizadas pelo projeto:
python -m pip install flask flask-sqlalchemy flask-login requests numpy scipy scikit-learn pyserial

Principais dependências
Biblioteca	Função
Flask	Aplicação web
Flask-SQLAlchemy	Integração com banco de dados
Flask-Login	Autenticação
Requests	Comunicação HTTP utilizada pelo simulador
NumPy	Processamento numérico
SciPy	Recursos científicos e matemáticos
Scikit-learn	Machine Learning
PySerial	Comunicação serial com o ESP32


⚠️ Importante: o pacote utilizado pelo projeto para comunicação serial é o PySerial. Portanto, o comando correto de instalação é pyserial, e não serial.

🧪 5. Validar o Ambiente Científico
Depois da instalação das dependências, verifique se os principais módulos científicos estão funcionando.
NumPy
python -c "import numpy; print('NumPy:', numpy.__version__)"

SciPy
python -c "import scipy; print('SciPy:', scipy.__version__)"

Scikit-learn
python -c "import sklearn; print('Scikit-learn:', sklearn.__version__)"

Teste geral
python -c "import numpy; import scipy; from sklearn.linear_model import LinearRegression; print('OK - ambiente científico funcionando')"

Se estiver tudo correto, será exibido:
OK - ambiente científico funcionando

▶️ Execução da Aplicação
6. Iniciar o Servidor Flask
Dentro da pasta do projeto, execute:
python app.py

A aplicação será executada localmente na porta 8080.
Acesse pelo navegador:
http://127.0.0.1:8080

⚠️ Importante: mantenha o terminal onde o app.py está sendo executado aberto enquanto estiver utilizando o sistema.

🧪 Execução do Simulador IoT
7. Executar o Simulador
O projeto possui um simulador IoT que permite gerar leituras sem a necessidade do ESP32 e do sensor físico.
Com o Flask já em execução, abra um segundo terminal na pasta do projeto:
python simulador_iot.py

O simulador irá gerar leituras de umidade e enviá-las para a aplicação.
Fluxo do simulador
┌──────────────────────┐
│    Simulador IoT     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       Flask          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       SQLite         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      Dashboard       │
└──────────────────────┘

O simulador é útil para:
- Testar o sistema;
- Validar o recebimento de dados;
- Testar os gráficos;
- Gerar histórico de leituras;
- Executar o projeto sem o hardware físico.
🔌 Execução com o ESP32
8. Conectar o ESP32
Para utilizar o sensor físico, conecte o ESP32 ao computador através de um cabo USB.
A comunicação utilizada atualmente pelo projeto é:
ESP32
  ↓
USB
  ↓
Porta Serial
  ↓
Python
  ↓
Flask

A implementação atual utiliza comunicação USB/Serial.
⚙️ 9. Configuração da Arduino IDE
Abra o código do ESP32 na Arduino IDE.
Placa
Selecione:
ESP32 Dev Module

Porta
No projeto, a porta utilizada é:
COM3

Para verificar a porta:
Arduino IDE
→ Ferramentas
→ Porta

Selecione a porta correspondente ao ESP32 conectado.
A porta pode variar de acordo com o computador. Caso o ESP32 apareça em outra porta, a configuração utilizada pelo Python deverá corresponder à porta correta.

📡 10. Configuração da Comunicação Serial
O ESP32 utiliza:
9600 baud

Portanto, ao abrir o Monitor Serial da Arduino IDE, utilize:
9600

O Python também utiliza essa mesma velocidade para realizar a leitura dos dados enviados pelo ESP32.

⬆️ 11. Carregar o Código no ESP32
Com a placa e a porta configuradas:
1. Conecte o ESP32 ao computador;
2. Selecione ESP32 Dev Module;
3. Selecione a porta correspondente;
4. Clique em Upload;
5. Aguarde o término da gravação.
Caso o Arduino IDE fique parado em:
Connecting........

pressione e mantenha pressionado o botão BOOT do ESP32 até o início da gravação.
Quando aparecer algo semelhante a:
Writing at...

o botão pode ser liberado.

📡 Comunicação entre ESP32 e Python
12. Formato dos Dados
O ESP32 realiza a leitura do sensor e envia os dados através da comunicação serial em formato JSON.
Exemplo:
{
  "umidade": 65,
  "valor_bruto": 2200,
  "status": "ADEQUADO"
}

Campos enviados
Campo	Descrição
umidade	Porcentagem calculada pelo ESP32
valor_bruto	Valor original da leitura analógica
status	Classificação da umidade


O Python utiliza a biblioteca PySerial para receber esses dados.

🌱 Calibração do Sensor
13. Valores Utilizados
A conversão da leitura analógica para porcentagem foi realizada utilizando uma calibração experimental.
Condição	Valor ADC	Umidade
Terra seca	3115	0%
Terra úmida	2415	50%
Terra muito úmida	1144	100%


Escala utilizada
3115 → 0%
2415 → 50%
1144 → 100%

A conversão é realizada por interpolação entre esses pontos.

⚠️ 14. Observação sobre a Calibração
A porcentagem apresentada pelo sistema representa uma escala relativa baseada na calibração experimental realizada para o protótipo.
Ela não deve ser interpretada como uma medição universal de umidade volumétrica do solo.
Os resultados podem variar de acordo com:
- Tipo de solo;
- Substrato;
- Profundidade do sensor;
- Características do sensor;
- Condições do ambiente.
Por isso, caso o sistema seja utilizado em outro cenário, uma nova calibração pode ser necessária.

🚦 Classificação da Umidade
O sistema classifica a umidade em três estados:
Faixa de Umidade	Status
< 30%	🔴 SECO
30% – 69%	🟢 ADEQUADO
≥ 70%	🔵 MUITO_UMIDO


Esses valores são parâmetros utilizados pelo protótipo para facilitar a interpretação das leituras.

🗄️ Fluxo de Dados do Sensor Físico
Quando o ESP32 está conectado, o fluxo completo é:
┌─────────────────────────┐
│   Sensor Capacitivo     │
│   de Umidade do Solo    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│          ESP32          │
│                         │
│ • Leitura ADC           │
│ • Conversão para %      │
│ • Geração do JSON       │
└────────────┬────────────┘
             │
             │ USB / Serial
             ▼
┌─────────────────────────┐
│         Python          │
│        PySerial         │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│         Flask           │
│        Aplicação        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│         SQLite          │
│      Banco de Dados     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│        Dashboard        │
│   Gráficos e Indicadores│
└─────────────────────────┘

🔄 Execução Completa com ESP32
Para executar o projeto utilizando o sensor físico:
Terminal 1 — Flask
python app.py

ESP32
Conecte o ESP32 ao computador através do USB.
Certifique-se de que:
Placa: ESP32 Dev Module
Porta: COM3
Serial: 9600 baud

Navegador
Acesse:
http://127.0.0.1:8080

O sistema deverá receber as leituras do sensor físico e apresentá-las no dashboard.

🧪 Execução Completa Apenas com o Simulador
Caso o ESP32 não esteja conectado, o sistema pode ser executado utilizando somente o simulador.
Terminal 1
python app.py

Terminal 2
python simulador_iot.py

Navegador
Acesse:
http://127.0.0.1:8080

O simulador continuará enviando dados para o sistema.

🔀 Execução com ESP32 + Simulador
O BioUrban permite manter as duas fontes de dados simultaneamente:
                         BIOURBAN
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
       🔌 SENSOR FÍSICO             🧪 SIMULADOR
            ESP32                       Python
              │                           │
              │ USB / Serial              │ HTTP
              │                           │
              └─────────────┬─────────────┘
                            │
                            ▼
                         Flask
                            │
                            ▼
                         SQLite
                            │
                            ▼
                       Dashboard

Dessa forma, o simulador não substitui o sensor físico. As duas fontes podem ser utilizadas para diferentes finalidades dentro do projeto.

🧪 Teste Manual da API
Também é possível testar a API sem utilizar o sensor físico.
Com o Flask em execução, utilize o PowerShell:
Invoke-RestMethod -Uri "http://127.0.0.1:8080/api/sensor_hidrico" -Method POST -ContentType "application/json" -Body '{"umidade":75.5,"fazenda_id":2}'

Uma resposta de sucesso será semelhante a:
status   umidade
------   -------
sucesso  75,5

Esse teste permite verificar se a API está funcionando corretamente antes de utilizar o sensor físico.

⚠️ Problemas Comuns
🔌 ESP32 não aparece na porta COM
Verifique:
- Cabo USB;
- Conexão física;
- Driver CP210x;
- Gerenciador de Dispositivos do Windows;
- Porta selecionada na Arduino IDE.

⬆️ Erro durante o upload do ESP32
Caso apareça:
Failed to connect to ESP32

ou:
Connecting........

sem iniciar a gravação:
1. Clique em Upload;
2. Aguarde aparecer Connecting...;
3. Pressione e mantenha pressionado o botão BOOT;
4. Aguarde aparecer o início da gravação;
5. Solte o botão.

🐍 Python não consegue acessar a COM3
Verifique se:
- O ESP32 está conectado;
- A porta correta foi selecionada;
- A porta utilizada pelo Python é a mesma do ESP32;
- O Monitor Serial da Arduino IDE está fechado.
⚠️ Importante: a mesma porta serial não deve ser utilizada simultaneamente pelo Monitor Serial da Arduino IDE e pelo Python.

📊 Dados aparecem no Monitor Serial, mas não no Dashboard
Verifique:
1. Se o app.py está em execução;
2. Se o ESP32 está conectado;
3. Se a porta serial está correta;
4. Se a velocidade está configurada como 9600;
5. Se o ESP32 está enviando os dados no formato JSON;
6. Se o banco de dados está sendo atualizado.

🖥️ OLED não funciona
Verifique as conexões:
OLED	ESP32
VDD	3V3
GND	GND
SDA	GPIO21
SCK/SCL	GPIO22


O endereço utilizado pelo display é:
0x3C

⚡ Alimentação do Hardware
Na configuração atual do projeto, o ESP32 é alimentado diretamente pelo cabo USB:
USB → ESP32

O sensor e o OLED utilizam a alimentação de 3V3 fornecida pelo ESP32.
⚠️ Atenção: não conecte uma fonte de 12V diretamente ao ESP32, OLED ou sensor.

⏱️ Intervalo de Leitura
O código atual do ESP32 realiza uma nova leitura a cada:
2 segundos

O intervalo é controlado pelo código através de:
delay(2000);

Esse valor pode ser alterado posteriormente conforme a necessidade do projeto.

📈 Exemplos de Leituras do Sensor
Durante os testes do protótipo foram obtidos valores como:
Condição	Leituras ADC
Terra seca	3120, 3117, 3108
Terra úmida	2430, 2415, 2400
Terra muito úmida	1152, 1139, 1142


Essas leituras foram utilizadas como base para a calibração experimental do sensor.

🧩 Origem dos Dados
O sistema diferencia as leituras de acordo com sua origem.

🔌 Sensor físico
Dados provenientes do ESP32 são identificados como:
sensor

🧪 Simulador
Dados gerados pelo simulador são identificados como:
simulador

Essa diferenciação permite visualizar e analisar separadamente as diferentes fontes de dados.
🎓 Aplicação no TCC
O BioUrban integra diferentes áreas da computação e tecnologia:
- Internet das Coisas (IoT);
- Sistemas embarcados;
- Programação em Python;
- Desenvolvimento web;
- APIs;
- Banco de dados;
- Comunicação serial;
- Sensores;
- Visualização de dados;
- Análise de dados;
- Machine Learning.
A integração entre o hardware e o software demonstra um fluxo completo de aquisição, processamento, armazenamento e visualização de dados.

🏗️ Arquitetura do Sistema
                              BIOURBAN
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
                 ▼                               ▼
        🔌 SENSOR FÍSICO                  🧪 SIMULADOR IoT
             ESP32                              Python
                 │                               │
                 │ USB / Serial                  │ HTTP
                 ▼                               ▼
              PySerial                         Flask
                 │                               │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                              SQLite
                                 │
                                 ▼
                             Dashboard
                                 │
                                 ▼
                         Análise dos Dados

📋 Resumo da Execução
🟢 Execução com Simulador
1. Instalar Python
        ↓
2. Instalar dependências
        ↓
3. Executar: python app.py
        ↓
4. Executar: python simulador_iot.py
        ↓
5. Acessar: http://127.0.0.1:8080

🔵 Execução com ESP32
1. Instalar Python
        ↓
2. Instalar dependências
        ↓
3. Configurar ESP32 na Arduino IDE
        ↓
4. Conectar ESP32 via USB
        ↓
5. Confirmar porta COM3
        ↓
6. Confirmar 9600 baud
        ↓
7. Executar: python app.py
        ↓
8. Acessar: http://127.0.0.1:8080

✅ Status do Projeto
Componente	Status
Aplicação Flask	✅
Dashboard	✅
Banco SQLite	✅
Simulador IoT	✅
API de umidade	✅
ESP32	✅
Sensor capacitivo	✅
Display OLED	✅
Comunicação USB/Serial	✅
PySerial	✅
Calibração experimental	✅
Integração físico + software	✅


👨‍💻 BioUrban Pro
Projeto acadêmico desenvolvido para integração de tecnologias IoT, sistemas embarcados, desenvolvimento web, análise de dados e monitoramento de cultivos urbanos.
Desenvolvido no contexto de Trabalho de Conclusão de Curso (TCC).

📄 Licença
Este projeto foi desenvolvido para fins acadêmicos e de pesquisa no contexto do Trabalho de Conclusão de Curso (TCC).