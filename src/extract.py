import pandas as pd
import requests

URL_SELIC = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados"


def extrair_selic():
    """Busca a meta Selic na API do Banco Central."""
    params = {"formato": "json", "dataInicial": "01/01/2024", "dataFinal": "31/12/2025"}
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0 (projeto-estudo)"}
    resposta = requests.get(URL_SELIC, params=params, headers=headers, timeout=30)
    resposta.raise_for_status()
    df = pd.DataFrame(resposta.json())
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = df["valor"].astype(float)
    df.to_csv("data/raw/selic.csv", index=False)
    return df


def extrair_csvs():
    clientes = pd.read_csv("data/raw/clientes.csv", parse_dates=["data_adesao"])
    cobrancas = pd.read_csv("data/raw/cobrancas.csv", parse_dates=["data_cobranca"])
    return clientes, cobrancas