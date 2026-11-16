"""Programa principal do Raspberry.

Lê o Arduino, calcula o risco, decide o relé, atualiza o LCD e grava no banco.
O site roda separado (web/app.py) e conversa com este programa pelo banco.

Uso:
    python coletor.py            # com o Arduino na USB
    python coletor.py --simular  # sem hardware, com leituras falsas
"""
import argparse
import signal
import sys
import time
from collections import deque

import banco
import config
import risco
from lcd import Display


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--simular", action="store_true", help="usa um Arduino falso")
    args = parser.parse_args()

    # O systemd para o serviço com SIGTERM; assim o finally roda e limpa o LCD
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    banco.criar_tabelas()
    banco.apagar_antigas(dias=7)

    if args.simular:
        from simulador import ArduinoSimulado
        arduino = ArduinoSimulado()
    else:
        from serial_arduino import ArduinoSerial
        arduino = ArduinoSerial(config.PORTA_SERIAL, config.BAUD)

    display = Display()
    display.escrever("Iniciando...")
    controle = risco.ControleRele()
    historico = deque(maxlen=1800)  # cerca de 1 hora de leituras
    nivel_anterior = None
    ligado_anterior = None
    ultima_chegada = time.time()
    offline = False
    dht_falhando = False

    banco.registrar_evento("inicio", "Coletor iniciado" + (" (simulação)" if args.simular else ""))

    try:
        while True:
            leitura = arduino.ler()
            agora = time.time()

            if leitura is None:
                if not offline and agora - ultima_chegada > config.TIMEOUT_ARDUINO_S:
                    offline = True
                    banco.registrar_evento("arduino_offline", "Sem leituras do Arduino")
                    display.mostrar_offline()
                continue

            if offline:
                offline = False
                banco.registrar_evento("arduino_online", "Arduino voltou a responder")
            ultima_chegada = agora
            leitura["ts"] = agora

            if (leitura["umid"] is None) != dht_falhando:
                dht_falhando = leitura["umid"] is None
                if dht_falhando:
                    banco.registrar_evento("falha_sensor", "DHT11 sem resposta")
                else:
                    banco.registrar_evento("sensor_ok", "DHT11 voltou a responder")

            cfg = banco.ler_config()
            pontos, nivel, sinais = risco.avaliar(leitura, historico, cfg)
            ligado = controle.decidir(nivel, agora, cfg)

            arduino.enviar(nivel, ligado)
            display.mostrar_estado(nivel, ligado)
            banco.salvar_leitura(leitura, pontos, nivel, ligado)
            historico.append(leitura)

            if nivel != nivel_anterior:
                detalhe = f" ({', '.join(sinais)})" if sinais else ""
                banco.registrar_evento("nivel", f"Risco {risco.NOMES[nivel]}{detalhe}")
            if ligado_anterior is not None and ligado != ligado_anterior:
                if ligado:
                    banco.registrar_evento("religamento", "Aparelhos religados")
                else:
                    banco.registrar_evento("desligamento", "Aparelhos desligados")
            nivel_anterior, ligado_anterior = nivel, ligado

    except KeyboardInterrupt:
        pass
    finally:
        banco.registrar_evento("parada", "Coletor parado")
        display.fechar()
        arduino.fechar()


if __name__ == "__main__":
    main()
