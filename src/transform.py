import pandas as pd
from validate import DATA_MAX


def tratar_cobrancas(cobrancas, clientes):
    """Limpa as cobranças. Devolve (cobrancas_limpas, rejeitadas, log)."""
    df = cobrancas.copy()
    log = {"linhas de entrada": len(df)}

    # 1) Duplicatas: mantém a primeira ocorrência de cada cobranca_id
    antes = len(df)
    df = df.drop_duplicates(subset="cobranca_id", keep="first")
    log["duplicatas removidas"] = antes - len(df)

    # 2) Datas no futuro: não dá para corrigir com segurança,
    #    então vão para quarentena (não são apagadas)
    futura = df["data_cobranca"] > DATA_MAX
    rejeitadas = df[futura].copy()
    rejeitadas["motivo"] = "data_futura"
    df = df[~futura].copy()
    log["linhas enviadas para quarentena (data futura)"] = len(rejeitadas)

    # 3) Valor nulo ou <= 0: recupera o valor da mensalidade do cliente
    invalido = df["valor"].isna() | (df["valor"] <= 0)
    valor_do_cliente = df["cliente_id"].map(clientes.set_index("cliente_id")["valor_mensal"])
    df.loc[invalido, "valor"] = valor_do_cliente[invalido]
    log["valores recuperados pela mensalidade do cliente"] = int(invalido.sum())

    log["linhas de saída"] = len(df)
    return df, rejeitadas, log