import sys
from pathlib import Path

import pytest

# permite importar os módulos da pasta raspberry/ nos testes
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def cfg():
    """Configuração padrão usada nos testes."""
    return {
        "modo": "auto",
        "rele_manual": True,
        "limite_chuva": 500,
        "subida_umidade": 5.0,
        "exigir_queda_temp": True,
        "janela_s": 60.0,
        "religar_apos_s": 30.0,
    }


@pytest.fixture
def banco_temp(tmp_path, monkeypatch):
    """Banco SQLite descartável, criado numa pasta temporária."""
    import banco
    import config

    monkeypatch.setattr(config, "BANCO", tmp_path / "teste.db")
    banco.criar_tabelas()
    return banco
