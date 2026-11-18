"""Site de monitoramento (Flask).

Roda separado do coletor e conversa com ele pelo banco: lê as leituras e
grava mudanças de modo, relé e limites, que o coletor aplica no ciclo seguinte.

Uso: python web/app.py  ->  http://<ip-do-raspberry>:5000
"""
import sys
import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import banco  # noqa: E402
import config  # noqa: E402
from risco import NOMES  # noqa: E402

app = Flask(__name__)

# limites que o site pode mudar e a faixa aceita para cada um
LIMITES = {
    "limite_chuva": (0, 1023),
    "subida_umidade": (1, 50),
    "janela_s": (10, 3600),
    "religar_apos_s": (5, 3600),
}


def _erro(mensagem):
    return jsonify(erro=mensagem), 400


@app.get("/")
def painel():
    return render_template("index.html")


@app.get("/api/estado")
def estado():
    leitura = banco.ultima_leitura()
    online = leitura is not None and time.time() - leitura["ts"] <= config.TIMEOUT_ARDUINO_S
    return jsonify(
        leitura=leitura,
        online=online,
        nome_nivel=NOMES[leitura["nivel"]] if leitura else None,
        config=banco.ler_config(),
    )


@app.get("/api/historico")
def historico():
    minutos = max(1, min(request.args.get("minutos", 30, type=int), 24 * 60))
    return jsonify(banco.leituras_desde(minutos * 60))


@app.get("/api/eventos")
def eventos():
    return jsonify(banco.ultimos_eventos(50))


@app.post("/api/modo")
def mudar_modo():
    modo = (request.get_json(silent=True) or {}).get("modo")
    if modo not in ("auto", "manual"):
        return _erro("modo deve ser auto ou manual")
    banco.salvar_config(modo=modo)
    banco.registrar_evento("config", f"Modo {'automático' if modo == 'auto' else 'manual'} pelo site")
    return jsonify(ok=True)


@app.post("/api/rele")
def mudar_rele():
    dados = request.get_json(silent=True) or {}
    if "ligado" not in dados:
        return _erro("informe ligado: true ou false")
    ligado = bool(dados["ligado"])
    # comandar o relé pelo site coloca o sistema em modo manual
    banco.salvar_config(modo="manual", rele_manual=ligado)
    banco.registrar_evento("config", f"Aparelhos {'ligados' if ligado else 'desligados'} pelo site")
    return jsonify(ok=True)


@app.post("/api/limites")
def mudar_limites():
    dados = request.get_json(silent=True) or {}
    novos = {}
    for chave, (minimo, maximo) in LIMITES.items():
        if chave not in dados:
            continue
        try:
            valor = float(dados[chave])
        except (TypeError, ValueError):
            return _erro(f"{chave} precisa ser um número")
        if not minimo <= valor <= maximo:
            return _erro(f"{chave} deve ficar entre {minimo} e {maximo}")
        novos[chave] = int(valor) if chave == "limite_chuva" else valor
    if "exigir_queda_temp" in dados:
        novos["exigir_queda_temp"] = bool(dados["exigir_queda_temp"])
    if not novos:
        return _erro("nenhum limite informado")
    banco.salvar_config(**novos)
    banco.registrar_evento("config", "Limites alterados pelo site")
    return jsonify(ok=True)


if __name__ == "__main__":
    banco.criar_tabelas()
    app.run(host="0.0.0.0", port=5000)
