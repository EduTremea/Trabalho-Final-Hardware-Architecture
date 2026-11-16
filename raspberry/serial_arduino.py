"""Comunicação com o Arduino pela USB serial."""
import glob
import time

import serial


def interpretar(linha):
    """Converte 'T:24.0;U:78;C:310' em dicionário.

    Retorna None se a linha vier incompleta ou quebrada.
    Quando o DHT falha, o Arduino manda -1 e aqui vira None.
    """
    try:
        partes = dict(p.split(":", 1) for p in linha.strip().split(";"))
        leitura = {
            "temp": float(partes["T"]),
            "umid": float(partes["U"]),
            "chuva": int(partes["C"]),
        }
    except (ValueError, KeyError):
        return None

    if leitura["umid"] < 0:
        leitura["temp"] = None
        leitura["umid"] = None
    return leitura


class ArduinoSerial:
    def __init__(self, porta=None, baud=9600):
        self.porta = porta
        self.baud = baud
        self.conexao = None

    def _achar_porta(self):
        portas = sorted(glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*"))
        return portas[0] if portas else None

    def conectar(self):
        porta = self.porta or self._achar_porta()
        if not porta:
            raise serial.SerialException("Arduino não encontrado nas portas USB")
        self.conexao = serial.Serial(porta, self.baud, timeout=1)
        time.sleep(2)  # abrir a porta reinicia o Arduino
        self.conexao.reset_input_buffer()
        print(f"Arduino conectado em {porta}")

    def ler(self):
        """Lê uma linha. Retorna a leitura ou None se não chegou nada válido."""
        try:
            if self.conexao is None:
                self.conectar()
            linha = self.conexao.readline().decode("ascii", errors="ignore")
        except (serial.SerialException, OSError):
            self.fechar()
            time.sleep(2)  # espera antes de tentar reconectar
            return None
        return interpretar(linha) if linha else None

    def enviar(self, nivel, aparelhos_ligados):
        if self.conexao is None:
            return
        comando = f"N:{nivel}\nR:{1 if aparelhos_ligados else 0}\n"
        try:
            self.conexao.write(comando.encode("ascii"))
        except (serial.SerialException, OSError):
            self.fechar()

    def fechar(self):
        if self.conexao is not None:
            try:
                self.conexao.close()
            except (serial.SerialException, OSError):
                pass
        self.conexao = None
