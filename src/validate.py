import pandas as pd

DATA_MAX = pd.Timestamp("2025-12-31")   # nenhuma cobrança pode ser depois disso
STATUS_VALIDOS = {"aprovada", "recusada", "pendente"}


def validar_cobrancas(cobrancas, clientes):
    """Roda as regras de qualidade e devolve quantas linhas violam cada uma."""
    checks = {
        "valor_nulo": cobrancas["valor"].isna().sum(),
        "valor_zero_ou_negativo": (cobrancas["valor"] <= 0).sum(),
        "id_duplicado": cobrancas["cobranca_id"].duplicated().sum(),
        "data_futura": (cobrancas["data_cobranca"] > DATA_MAX).sum(),
        "status_invalido": (~cobrancas["status"].isin(STATUS_VALIDOS)).sum(),
        "cliente_inexistente": (~cobrancas["cliente_id"].isin(clientes["cliente_id"])).sum(),
    }
    return {regra: int(qtd) for regra, qtd in checks.items()}


def salvar_relatorio(antes, depois, log, caminho="docs/relatorio_qualidade.md"):
    """Gera um relatório em Markdown com o antes e o depois do tratamento."""
    linhas = [
        "# Relatório de Qualidade de Dados\n",
        "| Regra | Antes | Depois |",
        "|---|---|---|",
    ]
    for regra in antes:
        linhas.append(f"| {regra} | {antes[regra]} | {depois[regra]} |")
    linhas.append("\n## Ações de tratamento\n")
    for acao, qtd in log.items():
        linhas.append(f"- {acao}: {qtd}")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))