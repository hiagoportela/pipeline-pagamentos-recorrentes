import sqlite3
from contextlib import closing

DB_PATH = "data/pagamentos.db"


def carregar(clientes, cobrancas, rejeitadas):
    """Grava as tabelas no SQLite. O SQLite é um banco em arquivo, sem instalar nada."""
    clientes = clientes.assign(data_adesao=clientes["data_adesao"].dt.strftime("%Y-%m-%d"))
    cobrancas = cobrancas.assign(data_cobranca=cobrancas["data_cobranca"].dt.strftime("%Y-%m-%d"))
    rejeitadas = rejeitadas.assign(data_cobranca=rejeitadas["data_cobranca"].dt.strftime("%Y-%m-%d"))

    with closing(sqlite3.connect(DB_PATH)) as conn:
        clientes.to_sql("clientes", conn, if_exists="replace", index=False)
        cobrancas.to_sql("cobrancas", conn, if_exists="replace", index=False)
        rejeitadas.to_sql("cobrancas_rejeitadas", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cobr_cliente ON cobrancas(cliente_id)")
        conn.commit()