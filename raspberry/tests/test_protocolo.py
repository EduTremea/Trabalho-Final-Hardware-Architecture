from serial_arduino import interpretar
from simulador import ArduinoSimulado


def test_linha_valida():
    assert interpretar("T:24.0;U:78;C:310\r\n") == {
        "temp": 24.0, "umid": 78.0, "chuva": 310,
    }


def test_linha_quebrada_retorna_none():
    assert interpretar("T:24.0;U:78") is None
    assert interpretar("lixo na serial") is None
    assert interpretar("") is None


def test_falha_no_dht_vira_none():
    leitura = interpretar("T:-1.0;U:-1;C:100")
    assert leitura["temp"] is None and leitura["umid"] is None
    assert leitura["chuva"] == 100


def test_simulador_gera_leituras_no_mesmo_formato():
    arduino = ArduinoSimulado(intervalo_s=0)
    leitura = arduino.ler()
    assert set(leitura) == {"temp", "umid", "chuva"}
    assert 0 <= leitura["chuva"] <= 1023
