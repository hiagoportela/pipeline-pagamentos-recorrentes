import csv
import logging
import sqlite3
import sys
from contextlib import closing
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/pagamentos.db")
HISTORICO = Path("docs/historico_monitoramento.csv")

# Limites do monitor (ficam no topo para ajustar fácil)
MAX_IDADE_HORAS = 24
ULTIMO_MES_ESPERADO = "2025-12"      # os dados simulados terminam aqui
LIMITE_VARIACAO_VOLUME_PCT = 20.0
FAIXA_APROVACAO_PCT = (80.0, 90.0)
LIMITE_QUARENTENA_PCT = 1.0

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("monitor")


def um_valor(conn, sql):
    return conn.execute(sql).fetchone()[0]


def coletar_metricas(conn):
    total = um_valor(conn, "SELECT COUNT(*) FROM cobrancas")
    rejeitadas = um_valor(conn, "SELECT COUNT(*) FROM cobrancas_rejeitadas")
    aprovadas = um_valor(conn, "SELECT COUNT(*) FROM cobrancas WHERE status = 'aprovada'")
    return {
        "total_cobrancas": total,
        "taxa_aprovacao_pct": round(100.0 * aprovadas / total, 2) if total else 0.0,
        "quarentena_pct": round(100.0 * rejeitadas / (total + rejeitadas), 2) if (total + rejeitadas) else 0.0,
        "valores_nulos": um_valor(conn, "SELECT COUNT(*) FROM cobrancas WHERE valor IS NULL"),
        "ids_duplicados": um_valor(conn, "SELECT COUNT(*) - COUNT(DISTINCT cobranca_id) FROM cobrancas"),
        "cobrancas_orfas": um_valor(
            conn,
            "SELECT COUNT(*) FROM cobrancas WHERE cliente_id NOT IN (SELECT cliente_id FROM clientes)",
        ),
        "ultimo_mes": um_valor(conn, "SELECT MAX(strftime('%Y-%m', data_cobranca)) FROM cobrancas"),
    }


def ler_ultimo_total():
    """Volume da execução anterior, para comparar com a atual."""
    if not HISTORICO.exists():
        return None
    with open(HISTORICO, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    return int(linhas[-1]["total_cobrancas"]) if linhas else None


def avaliar(m, idade_horas, total_anterior):
    baixo, alto = FAIXA_APROVACAO_PCT
    checks = [
        ("pipeline_atualizado", idade_horas <= MAX_IDADE_HORAS,
         f"banco atualizado há {idade_horas:.1f}h (limite {MAX_IDADE_HORAS}h)"),
        ("dados_ate_mes_esperado", m["ultimo_mes"] == ULTIMO_MES_ESPERADO,
         f"último mês nos dados: {m['ultimo_mes']} (esperado {ULTIMO_MES_ESPERADO})"),
        ("sem_valores_nulos", m["valores_nulos"] == 0, f"{m['valores_nulos']} valores nulos"),
        ("sem_ids_duplicados", m["ids_duplicados"] == 0, f"{m['ids_duplicados']} IDs duplicados"),
        ("sem_cobrancas_orfas", m["cobrancas_orfas"] == 0, f"{m['cobrancas_orfas']} cobranças sem cliente"),
        ("taxa_aprovacao_na_faixa", baixo <= m["taxa_aprovacao_pct"] <= alto,
         f"aprovação em {m['taxa_aprovacao_pct']}% (faixa {baixo}-{alto}%)"),
        ("quarentena_baixa", m["quarentena_pct"] <= LIMITE_QUARENTENA_PCT,
         f"quarentena em {m['quarentena_pct']}% (limite {LIMITE_QUARENTENA_PCT}%)"),
    ]
    if total_anterior:
        variacao = abs(100.0 * (m["total_cobrancas"] - total_anterior) / total_anterior)
        checks.append(("volume_estavel", variacao <= LIMITE_VARIACAO_VOLUME_PCT,
                       f"volume variou {variacao:.1f}% desde a última execução"))
    else:
        log.info("Primeira execução: sem histórico para comparar o volume.")
    return checks


def registrar_historico(m, status):
    novo = not HISTORICO.exists()
    with open(HISTORICO, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["data_hora", "total_cobrancas", "taxa_aprovacao_pct", "quarentena_pct", "status"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), m["total_cobrancas"],
                    m["taxa_aprovacao_pct"], m["quarentena_pct"], status])


def main():
    if not DB_PATH.exists():
        log.error("Banco não encontrado em %s. O pipeline rodou?", DB_PATH)
        sys.exit(1)

    idade_horas = (datetime.now() - datetime.fromtimestamp(DB_PATH.stat().st_mtime)).total_seconds() / 3600

    with closing(sqlite3.connect(DB_PATH)) as conn:
        metricas = coletar_metricas(conn)

    checks = avaliar(metricas, idade_horas, ler_ultimo_total())
    falhas = [nome for nome, ok, _ in checks if not ok]

    for nome, ok, detalhe in checks:
        log.log(logging.INFO if ok else logging.ERROR, "[%s] %s: %s", "OK" if ok else "FALHA", nome, detalhe)

    registrar_historico(metricas, "FALHA" if falhas else "OK")

    if falhas:
        log.error("ALERTA: %d verificação(ões) falharam: %s", len(falhas), ", ".join(falhas))
        sys.exit(1)
    log.info("Todas as verificações passaram.")


if __name__ == "__main__":
    main()