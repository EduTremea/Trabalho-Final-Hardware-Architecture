from risco import ATENCAO, NORMAL, TEMPESTADE, ControleRele, avaliar


def leitura(ts, temp=26.0, umid=60.0, chuva=30):
    return {"ts": ts, "temp": temp, "umid": umid, "chuva": chuva}


def test_tempo_bom_fica_normal(cfg):
    historico = [leitura(t) for t in range(0, 60, 2)]
    pontos, nivel, sinais = avaliar(leitura(60), historico, cfg)
    assert (pontos, nivel, sinais) == (0, NORMAL, [])


def test_so_chuva_da_atencao(cfg):
    historico = [leitura(t) for t in range(0, 60, 2)]
    pontos, nivel, _ = avaliar(leitura(60, chuva=700), historico, cfg)
    assert (pontos, nivel) == (2, ATENCAO)


def test_chuva_e_umidade_subindo_da_tempestade(cfg):
    historico = [leitura(0, umid=60, temp=26)]
    pontos, nivel, sinais = avaliar(leitura(30, umid=70, temp=24, chuva=700), historico, cfg)
    assert (pontos, nivel) == (3, TEMPESTADE)
    assert sinais == ["umidade subiu", "chuva"]


def test_so_umidade_continua_normal(cfg):
    historico = [leitura(0, umid=60, temp=26)]
    pontos, nivel, _ = avaliar(leitura(30, umid=70, temp=24), historico, cfg)
    assert (pontos, nivel) == (1, NORMAL)


def test_umidade_sem_esfriar_nao_conta_quando_exigido(cfg):
    historico = [leitura(0, umid=60, temp=26)]
    _, _, sinais = avaliar(leitura(30, umid=70, temp=27), historico, cfg)
    assert "umidade subiu" not in sinais


def test_umidade_conta_quando_queda_de_temperatura_nao_e_exigida(cfg):
    cfg["exigir_queda_temp"] = False
    historico = [leitura(0, umid=60, temp=26)]
    _, _, sinais = avaliar(leitura(30, umid=70, temp=27), historico, cfg)
    assert "umidade subiu" in sinais


def test_leitura_fora_da_janela_e_ignorada(cfg):
    historico = [leitura(0, umid=50, temp=26)]
    _, _, sinais = avaliar(leitura(120, umid=70, temp=24), historico, cfg)
    assert "umidade subiu" not in sinais


def test_falha_no_dht_nao_quebra_a_regra(cfg):
    historico = [leitura(0)]
    atual = leitura(30, temp=None, umid=None, chuva=700)
    pontos, nivel, _ = avaliar(atual, historico, cfg)
    assert (pontos, nivel) == (2, ATENCAO)


def test_rele_desliga_na_tempestade_e_religa_depois_do_tempo(cfg):
    controle = ControleRele()
    assert controle.decidir(TEMPESTADE, 0, cfg) is False
    assert controle.decidir(NORMAL, 10, cfg) is False   # começou a contar
    assert controle.decidir(NORMAL, 30, cfg) is False   # 20 s, ainda não
    assert controle.decidir(NORMAL, 40, cfg) is True    # 30 s, religa


def test_atencao_zera_a_contagem_para_religar(cfg):
    controle = ControleRele()
    controle.decidir(TEMPESTADE, 0, cfg)
    controle.decidir(NORMAL, 10, cfg)
    controle.decidir(ATENCAO, 30, cfg)
    assert controle.decidir(NORMAL, 45, cfg) is False   # recomeçou em 45


def test_modo_manual_obedece_o_site(cfg):
    controle = ControleRele()
    cfg["modo"] = "manual"
    cfg["rele_manual"] = False
    assert controle.decidir(NORMAL, 0, cfg) is False
    cfg["rele_manual"] = True
    assert controle.decidir(TEMPESTADE, 2, cfg) is True
