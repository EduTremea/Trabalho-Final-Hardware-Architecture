"""Acesso ao banco SQLite.

O coletor grava leituras e eventos; o site lê os dados e muda a configuração.
"""
import sqlite3
import time
from contextlib import contextmanager

import config


@contextmanager
def abrir():
    config.BANCO.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(config.BANCO, timeout=5)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")  # permite ler e gravar ao mesmo tempo
    try:
        yield con
        con.commit()
    finally:
        con.close()


def criar_tabelas():
    with abrir() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS leituras (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                ts     REAL NOT NULL,
                temp   REAL,
                umid   REAL,
                chuva  INTEGER,
                pontos INTEGER,
                nivel  INTEGER,
                rele   INTEGER
            );
            CREATE INDEX IF NOT EXISTS idx_leituras_ts ON leituras(ts);

            CREATE TABLE IF NOT EXISTS eventos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        REAL NOT NULL,
                tipo      TEXT NOT NULL,
                descricao TEXT
            );

            CREATE TABLE IF NOT EXISTS config (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            );
            """
        )
        for chave, valor in config.PADROES.items():
            con.execute("INSERT OR IGNORE INTO config (chave, valor) VALUES (?, ?)", (chave, valor))


# ---------- leituras ----------

def salvar_leitura(leitura, pontos, nivel, aparelhos_ligados):
    with abrir() as con:
        con.execute(
            "INSERT INTO leituras (ts, temp, umid, chuva, pontos, nivel, rele) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (leitura["ts"], leitura["temp"], leitura["umid"],
             leitura["chuva"], pontos, nivel, int(aparelhos_ligados)),
        )


def ultima_leitura():
    with abrir() as con:
        linha = con.execute("SELECT * FROM leituras ORDER BY ts DESC LIMIT 1").fetchone()
    return dict(linha) if linha else None


def leituras_desde(segundos):
    limite = time.time() - segundos
    with abrir() as con:
        linhas = con.execute("SELECT * FROM leituras WHERE ts >= ? ORDER BY ts", (limite,)).fetchall()
    return [dict(l) for l in linhas]


def apagar_antigas(dias=7):
    limite = time.time() - dias * 86400
    with abrir() as con:
        con.execute("DELETE FROM leituras WHERE ts < ?", (limite,))


# ---------- eventos ----------

def registrar_evento(tipo, descricao=""):
    with abrir() as con:
        con.execute("INSERT INTO eventos (ts, tipo, descricao) VALUES (?, ?, ?)", (time.time(), tipo, descricao))


def ultimos_eventos(limite=50):
    with abrir() as con:
        linhas = con.execute("SELECT * FROM eventos ORDER BY ts DESC LIMIT ?", (limite,)).fetchall()
    return [dict(l) for l in linhas]


# ---------- configuração ----------

def ler_config():
    with abrir() as con:
        salvos = {l["chave"]: l["valor"] for l in con.execute("SELECT chave, valor FROM config")}
    bruto = {**config.PADROES, **salvos}
    return {
        "modo": bruto["modo"],
        "rele_manual": bruto["rele_manual"] == "1",
        "limite_chuva": int(float(bruto["limite_chuva"])),
        "subida_umidade": float(bruto["subida_umidade"]),
        "exigir_queda_temp": bruto["exigir_queda_temp"] == "1",
        "janela_s": float(bruto["janela_s"]),
        "religar_apos_s": float(bruto["religar_apos_s"]),
    }


def salvar_config(**valores):
    with abrir() as con:
        for chave, valor in valores.items():
            if chave not in config.PADROES:
                raise KeyError(f"configuração desconhecida: {chave}")
            if isinstance(valor, bool):
                valor = "1" if valor else "0"
            con.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES (?, ?)", (chave, str(valor)))
