import requests
import time
import random
from datetime import datetime

# Configurações base
URL_API = "http://127.0.0.1:8080/api/sensor_hidrico"

def simular_envio():
    print("="*50)
    print("      BIOURBAN - SIMULADOR DE SENSOR IOT")
    print("="*50)
    
    # Solicita o ID da fazenda dinamicamente
    try:
        fazenda_id = int(input("Digite o ID da fazenda (veja na URL do navegador): "))
    except ValueError:
        print("Erro: O ID deve ser um número inteiro.")
        return

    print(f"\nConectando à API para a Fazenda #{fazenda_id}...")
    print("Pressione CTRL+C para interromper a simulação.\n")
    
    try:
        while True:
            # Simula um consumo entre 0.5 e 3.0 litros
            consumo_atual = round(random.uniform(0.5, 3.0), 2)
            
            payload = {
                "consumo": consumo_atual,
                "fazenda_id": fazenda_id
            }
            
            try:
                response = requests.post(URL_API, json=payload)
                
                if response.status_code == 201:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sucesso! Enviado: {consumo_atual}L")
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