import random
from datetime import date, timedelta
import pandas as pd

random.seed(42)  # garante que os dados sejam os mesmos a cada execução

SETORES = ["energia", "agua", "telecom", "streaming"]
ESTADOS = ["RJ", "SP", "MG", "BA", "RS", "PE"]


def gerar_clientes(n=2000):
    linhas = []
    for i in range(1, n + 1):
        linhas.append({
            "cliente_id": i,
            "estado": random.choice(ESTADOS),
            "setor": random.choice(SETORES),
            "data_adesao": date(2024, 1, 1) + timedelta(days=random.randint(0, 540)),
            "valor_mensal": round(random.uniform(30, 400), 2),
        })
    return pd.DataFrame(linhas)


def gerar_cobrancas(clientes):
    linhas = []
    cobranca_id = 1
    fim = date(2025, 12, 1)
    for c in clientes.itertuples():
        mes = c.data_adesao.replace(day=1)
        while mes <= fim:
            status = random.choices(
                ["aprovada", "recusada", "pendente"], [0.85, 0.10, 0.05]
            )[0]
            linhas.append({
                "cobranca_id": cobranca_id,
                "cliente_id": c.cliente_id,
                "data_cobranca": mes + timedelta(days=9),
                "valor": c.valor_mensal,
                "status": status,
            })
            cobranca_id += 1
            if random.random() < 0.02:  # 2% de chance de cancelar (churn)
                break
            mes = (mes + timedelta(days=32)).replace(day=1)
    return pd.DataFrame(linhas)


def sujar_dados(df):
    """Injeta problemas reais de qualidade para a validação ter o que pegar."""
    df = df.copy()
    df.loc[df.sample(frac=0.010, random_state=1).index, "valor"] = None       # nulos
    df.loc[df.sample(frac=0.005, random_state=2).index, "valor"] = -50.0      # negativos
    df.loc[df.sample(frac=0.003, random_state=3).index, "data_cobranca"] = date(2030, 1, 1)  # data futura
    duplicadas = df.sample(frac=0.005, random_state=4)
    return pd.concat([df, duplicadas], ignore_index=True)                     # duplicatas


if __name__ == "__main__":
    clientes = gerar_clientes()
    cobrancas = sujar_dados(gerar_cobrancas(clientes))
    clientes.to_csv("data/raw/clientes.csv", index=False)
    cobrancas.to_csv("data/raw/cobrancas.csv", index=False)
    print(f"{len(clientes)} clientes e {len(cobrancas)} cobranças gerados.")