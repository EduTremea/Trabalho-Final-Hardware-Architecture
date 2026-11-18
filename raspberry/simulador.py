"""Arduino falso, para testar o sistema sem hardware.

Tem os mesmos métodos do ArduinoSerial (ler, enviar, fechar) e repete um
ciclo de 3 minutos: tempo bom, céu fechando, chuva forte e melhora.
"""
import random
import time


def _mistura(a, b, f):
    f = max(0.0, min(1.0, f))
    return a + (b - a) * f


class ArduinoSimulado:
    def __init__(self, ciclo_s=180, intervalo_s=2):
        self.inicio = time.time()
        self.ciclo_s = ciclo_s
        self.intervalo_s = intervalo_s
        self.nivel = 0
        self.aparelhos_ligados = True

    def _intensidade(self, fase):
        """0 = tempo bom, 1 = tempestade, de acordo com a fase do ciclo (0 a 1)."""
        if fase < 0.40:
            return 0.0
        if fase < 0.50:
            return (fase - 0.40) / 0.10   # céu fechando
        if fase < 0.75:
            return 1.0                    # chuva forte
        if fase < 0.85:
            return 1 - (fase - 0.75) / 0.10  # melhorando
        return 0.0

    def ler(self):
        time.sleep(self.intervalo_s)
        fase = ((time.time() - self.inicio) % self.ciclo_s) / self.ciclo_s
        f = self._intensidade(fase)
        chovendo = 0.50 <= fase < 0.75
        return {
            "temp": float(round(_mistura(27, 23, f))),   # o DHT11 só mede inteiros
            "umid": float(round(_mistura(58, 78, f))),
            "chuva": int(random.uniform(650, 850) if chovendo else random.uniform(20, 60)),
        }

    def enviar(self, nivel, aparelhos_ligados):
        self.nivel = nivel
        self.aparelhos_ligados = aparelhos_ligados

    def fechar(self):
        pass
