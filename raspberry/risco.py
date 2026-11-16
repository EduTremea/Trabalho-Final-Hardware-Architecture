"""Regra de risco e controle dos aparelhos.

Não usa hardware nem banco, então dá para testar no próprio PC.
"""

NORMAL, ATENCAO, TEMPESTADE = 0, 1, 2
NOMES = {NORMAL: "NORMAL", ATENCAO: "ATENCAO", TEMPESTADE: "TEMPESTADE"}


def avaliar(leitura, historico, cfg):
    """Calcula os pontos de risco da leitura atual.

    leitura: dict com ts, temp, umid e chuva
    historico: leituras anteriores no mesmo formato, mais antigas primeiro
    cfg: limites lidos do banco

    Pontos: umidade subiu (com queda de temperatura) = 1, chuva = 2.
    Só chuva = atenção; chuva com umidade subindo = tempestade.
    Retorna (pontos, nivel, sinais).
    """
    janela = [h for h in historico if leitura["ts"] - h["ts"] <= cfg["janela_s"]]
    pontos = 0
    sinais = []

    # Umidade subindo; a temperatura caindo junto é opcional (cfg)
    com_dht = [h for h in janela if h["umid"] is not None]
    if com_dht and leitura["umid"] is not None:
        antiga = com_dht[0]
        subiu = leitura["umid"] - antiga["umid"] >= cfg["subida_umidade"]
        esfriou = leitura["temp"] < antiga["temp"]
        if subiu and (esfriou or not cfg["exigir_queda_temp"]):
            pontos += 1
            sinais.append("umidade subiu")

    # Chuva detectada pelo higrômetro
    if leitura["chuva"] >= cfg["limite_chuva"]:
        pontos += 2
        sinais.append("chuva")

    if pontos >= 3:
        nivel = TEMPESTADE
    elif pontos == 2:
        nivel = ATENCAO
    else:
        nivel = NORMAL
    return pontos, nivel, sinais


class ControleRele:
    """Decide se os aparelhos ficam ligados.

    No modo automático, desliga na tempestade e só religa depois de passar
    um tempo seguido em nível normal. No manual, obedece o site.
    """

    def __init__(self):
        self.ligado = True
        self.normal_desde = None

    def decidir(self, nivel, agora, cfg):
        if cfg["modo"] == "manual":
            self.ligado = cfg["rele_manual"]
            self.normal_desde = None
            return self.ligado

        if nivel == TEMPESTADE:
            self.ligado = False
            self.normal_desde = None
        elif not self.ligado:
            if nivel == NORMAL:
                if self.normal_desde is None:
                    self.normal_desde = agora
                if agora - self.normal_desde >= cfg["religar_apos_s"]:
                    self.ligado = True
                    self.normal_desde = None
            else:
                self.normal_desde = None  # voltou para atenção, zera a contagem
        return self.ligado
