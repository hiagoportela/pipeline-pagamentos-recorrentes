import logging
import sys

from extract import extrair_csvs, extrair_selic
from validate import validar_cobrancas, salvar_relatorio
from transform import tratar_cobrancas
from load import carregar

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("pipeline")


def main():
    log.info("Etapa 1/5: extração")
    clientes, cobrancas = extrair_csvs()
    try:
        selic = extrair_selic()
        log.info("Selic extraída da API do BCB: %d registros", len(selic))
    except Exception as erro:
        log.warning("Falha ao extrair a Selic (o pipeline continua): %s", erro)

    log.info("Etapa 2/5: validação dos dados brutos")
    antes = validar_cobrancas(cobrancas, clientes)
    log.info("Problemas encontrados: %s", antes)

    log.info("Etapa 3/5: tratamento")
    limpas, rejeitadas, acoes = tratar_cobrancas(cobrancas, clientes)

    log.info("Etapa 4/5: validação dos dados tratados")
    depois = validar_cobrancas(limpas, clientes)
    log.info("Problemas restantes: %s", depois)
    salvar_relatorio(antes, depois, acoes)

    if sum(depois.values()) > 0:
        log.error("Ainda há problemas de qualidade. Carga cancelada.")
        sys.exit(1)

    log.info("Etapa 5/5: carga no banco")
    carregar(clientes, limpas, rejeitadas)
    log.info("Pipeline concluído com sucesso.")


if __name__ == "__main__":
    main()