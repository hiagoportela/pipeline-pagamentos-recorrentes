import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

pd.set_option("display.width", 200)


def main():
    Path("docs/resultados").mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect("data/pagamentos.db")) as conn:
        for arquivo in sorted(Path("sql").glob("*.sql")):
            df = pd.read_sql_query(arquivo.read_text(encoding="utf-8"), conn)
            print(f"\n=== {arquivo.stem} ===")
            print(df.head(15).to_string(index=False))
            df.to_csv(f"docs/resultados/{arquivo.stem}.csv", index=False)


if __name__ == "__main__":
    main()