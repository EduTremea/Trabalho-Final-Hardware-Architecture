"""Configurações do lado do Raspberry Pi."""
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
BANCO = Path(os.environ.get("TEMPESTADE_DB", BASE / "dados" / "tempestade.db"))

# Porta serial do Arduino. O Uno original costuma aparecer como /dev/ttyACM0
# e os clones com CH340 como /dev/ttyUSB0. None = procura sozinho.
PORTA_SERIAL = None
BAUD = 9600

# Pinos do LCD na numeração física da placa (modo BOARD)
LCD_RS = 37
LCD_E = 35
LCD_DADOS = [33, 31, 29, 23]  # D4, D5, D6, D7

# Sem leitura do Arduino por mais que isso, ele é considerado offline
TIMEOUT_ARDUINO_S = 10

# Valores iniciais. Depois de criado o banco, o site é quem altera.
PADROES = {
    "modo": "auto",            # auto ou manual
    "rele_manual": "1",        # só vale no modo manual (1 = aparelhos ligados)
    "limite_chuva": "500",     # 0 a 1023; a partir disso conta como chuva
    "subida_umidade": "5",     # pontos de umidade que precisam subir na janela
    "exigir_queda_temp": "1",  # 1 = a umidade só conta se a temperatura cair junto
    "janela_s": "60",          # tamanho da janela de comparação, em segundos
    "religar_apos_s": "30",    # tempo em nível normal antes de religar sozinho
}
