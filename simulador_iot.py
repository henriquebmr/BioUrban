import requests
import time
import random
from datetime import datetime

# Configurações base
URL_API = "http://127.0.0.1:8080/api/sensor_hidrico"

# ==========================================
# CALIBRAÇÃO EXPERIMENTAL DO SENSOR
# ==========================================

ADC_SECO = 3115
ADC_UMIDO = 2415
ADC_MUITO_UMIDO = 1144


def converter_adc_para_porcentagem(adc_val):
    """
    Converte a leitura ADC para porcentagem
    utilizando a mesma calibração experimental
    definida para o ESP32 físico.

    3115 ADC -> 0%
    2415 ADC -> 50%
    1144 ADC -> 100%

    Quanto menor o ADC, maior a umidade.
    """

    if adc_val >= ADC_SECO:

        porcentagem = 0.0

    elif adc_val >= ADC_UMIDO:

        # 3115 -> 0%
        # 2415 -> 50%

        porcentagem = (
            (ADC_SECO - adc_val)
            / (ADC_SECO - ADC_UMIDO)
        ) * 50.0

    else:

        # 2415 -> 50%
        # 1144 -> 100%

        porcentagem = 50.0 + (
            (ADC_UMIDO - adc_val)
            / (ADC_UMIDO - ADC_MUITO_UMIDO)
        ) * 50.0

    return round(max(0.0, min(100.0, porcentagem)), 1)

def simular_envio():
    print("="*55)
    print("      BIOURBAN - SIMULADOR IOT REALISTA (ESP32)")
    print("="*55)
    
    # Solicita o ID da fazenda dinamicamente
    try:
        fazenda_id = int(input("Digite o ID da fazenda (veja na URL do navegador): "))
    except ValueError:
        print("Erro: O ID deve ser um número inteiro.")
        return

    print(f"\nSimulando lecturas de hardware real para a Fazenda #{fazenda_id}...")
    print(f"Parâmetros de calibração: 0% = {ADC_SECO} | 50% = {ADC_UMIDO} | 100% = {ADC_MUITO_UMIDO}")
    print("Pressione CTRL+C para interromper a simulação.\n")
    
    try:
        while True:
            # Simula a leitura analógica bruta do ADC do ESP32.
            # Faixa variando entre Terra Seca (2945) e Terra Muito Úmida (1400)
            adc_simulado = random.randint(ADC_MUITO_UMIDO, ADC_SECO)
            
            # Converte a leitura analógica para porcentagem com base na calibração
            porcentagem = converter_adc_para_porcentagem(adc_simulado)
            
            payload = {
                "umidade": porcentagem,
                "fazenda_id": fazenda_id
            }
            
            try:
                response = requests.post(URL_API, json=payload)
                
                if response.status_code == 201:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] RAW ADC: {adc_simulado} -> Enviado: {porcentagem}%")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro na API: Status {response.status_code}")
            
            except requests.exceptions.ConnectionError:
                print("Erro: Não foi possível conectar ao servidor. O app.py está rodando?")
            
            # ESPERA 1 MINUTO (60 SEGUNDOS) PARA O PRÓXIMO ENVIO
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n\nSimulação finalizada pelo usuário.")

if __name__ == "__main__":
    simular_envio()