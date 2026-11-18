import time


def test_config_padrao_e_alteracao(banco_temp):
    cfg = banco_temp.ler_config()
    assert cfg["modo"] == "auto" and cfg["limite_chuva"] == 500

    banco_temp.salvar_config(modo="manual", rele_manual=False, limite_chuva=650)
    cfg = banco_temp.ler_config()
    assert cfg["modo"] == "manual" and cfg["rele_manual"] is False and cfg["limite_chuva"] == 650


def test_salva_e_le_leituras(banco_temp):
    agora = time.time()
    banco_temp.salvar_leitura({"ts": agora, "temp": 25.0, "umid": 60.0, "chuva": 40}, 0, 0, True)
    ultima = banco_temp.ultima_leitura()
    assert ultima["chuva"] == 40 and ultima["rele"] == 1
    assert len(banco_temp.leituras_desde(60)) == 1


def test_api_do_site(banco_temp):
    from web.app import app

    cliente = app.test_client()
    assert cliente.get("/api/estado").get_json()["leitura"] is None

    assert cliente.post("/api/rele", json={"ligado": False}).status_code == 200
    cfg = banco_temp.ler_config()
    assert cfg["modo"] == "manual" and cfg["rele_manual"] is False

    assert cliente.post("/api/limites", json={"limite_chuva": 2000}).status_code == 400
    assert cliente.post("/api/limites", json={"limite_chuva": 600}).status_code == 200
    assert banco_temp.ler_config()["limite_chuva"] == 600

    assert cliente.post("/api/modo", json={"modo": "turbo"}).status_code == 400
    assert len(cliente.get("/api/eventos").get_json()) >= 2
