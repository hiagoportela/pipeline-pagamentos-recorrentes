import sqlite3
from contextlib import closing

with closing(sqlite3.connect("data/pagamentos.db")) as conn:
    conn.execute("UPDATE cobrancas SET valor = NULL WHERE cobranca_id <= 50")
    conn.execute("UPDATE cobrancas SET cliente_id = 999999 WHERE cobranca_id BETWEEN 51 AND 80")
    conn.commit()
print("Falhas injetadas: valores nulos e cobranças órfãs.")