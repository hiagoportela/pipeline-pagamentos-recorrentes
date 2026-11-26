# Pipeline de Pagamentos Recorrentes

Projeto de dados de ponta a ponta que simula o ciclo de vida do dado em um negócio
de cobranças recorrentes: extração de múltiplas fontes, tratamento, validação de
qualidade, carga, análises de negócio em SQL e monitoramento.

> **Os dados de clientes e cobranças são sintéticos**, gerados por `src/generate_data.py`
> com problemas de qualidade injetados de propósito. Os números das análises demonstram
> o método e não representam nenhum negócio real.

## O que o projeto faz

```
Fontes (CSV de clientes, CSV de cobranças, API Selic/BCB)
   → Validação dos dados brutos
   → Tratamento (duplicatas, valores inválidos, quarentena)
   → Validação dos dados tratados (portão de qualidade)
   → Carga no SQLite
   → Análises SQL + Monitoramento
```

## Estrutura

```
src/        pipeline (extract, validate, transform, load, run_pipeline),
            análises (run_queries) e monitoramento (monitor, simular_falha)
sql/        consultas de negócio
docs/       relatório de qualidade, histórico de monitoramento e diário de IA
```

## Decisões de projeto

- **Validar antes e depois do tratamento.** O relatório `docs/relatorio_qualidade.md`
  mostra o que havia de errado e prova que foi corrigido.
- **Quarentena em vez de exclusão.** Cobranças com data futura não têm correção segura;
  vão para a tabela `cobrancas_rejeitadas` para investigação.
- **Portão de qualidade.** Se a validação final encontrar problemas, a carga é cancelada
  e o pipeline termina com código de erro.
- **Falha isolada da API.** Se a API da Selic falhar, o pipeline segue e registra o aviso.
  Isso aconteceu de verdade durante o desenvolvimento (erro 406) e o pipeline continuou.
- **Valor inválido recuperado pela mensalidade do cliente.** É uma regra de negócio
  assumida; em um caso real, seria confirmada com o dono do dado.

## Resultados da qualidade de dados

| Regra | Antes | Depois |
|---|---|---|
| Valores nulos | 266 | 0 |
| Valores zero ou negativos | 133 | 0 |
| IDs de cobrança duplicados | 132 | 0 |
| Datas futuras | 79 | 0 |
| Status inválido | 0 | 0 |
| Cliente inexistente | 0 | 0 |

Reconciliação: 26.620 linhas de entrada − 132 duplicatas − 79 em quarentena = 26.409
linhas carregadas. Outras 396 linhas (1,5%) tiveram o valor recuperado pela mensalidade
do cliente.

## Análises SQL

| Arquivo | Pergunta de negócio | Técnicas |
|---|---|---|
| `aprovacao_mensal.sql` | Taxa de aprovação por mês | agregação, CASE WHEN |
| `recusa_por_setor.sql` | Recusas e valor recusado por setor | JOIN |
| `churn_mensal.sql` | Clientes ativos e cancelados por mês | CTEs, LEFT JOIN |
| `receita_mensal_variacao.sql` | Receita aprovada e variação mensal | window function (LAG) |

**Conferência dos resultados contra o gerador:** a taxa de aprovação oscilou entre 81,7%
e 88,2% nos primeiros 15 meses, em linha com os 85% configurados na simulação. A taxa de
recusa ficou entre 9,6% e 9,8% em todos os setores, o que é esperado, já que o gerador usa
a mesma probabilidade para todos. Ou seja, o SQL reproduz o que foi simulado.

**Atenção ao interpretar a receita:** o crescimento alto nos primeiros meses (por exemplo,
+79% em fev/2024) vem de a base de clientes começar do zero e ir crescendo na simulação.
Não é um achado de negócio.

## Monitoramento

`src/monitor.py` checa a saúde do banco: atualização, último mês dos dados, nulos,
duplicados, cobranças órfãs, faixa da taxa de aprovação, % em quarentena e variação
de volume. Cada execução entra em `docs/historico_monitoramento.csv`, e uma falha
termina o script com código 1.

Teste do alerta: `src/simular_falha.py` injeta problemas no banco e o monitor os detecta.

```
[OK]    sem_valores_nulos: 0 valores nulos
[OK]    sem_cobrancas_orfas: 0 cobranças sem cliente
        ... (injeção de falhas) ...
[FALHA] sem_valores_nulos: 49 valores nulos
[FALHA] sem_cobrancas_orfas: 30 cobranças sem cliente
ALERTA: 2 verificação(ões) falharam: sem_valores_nulos, sem_cobrancas_orfas
        ... (pipeline reexecutado) ...
[OK]    sem_valores_nulos: 0 valores nulos
[OK]    sem_cobrancas_orfas: 0 cobranças sem cliente
Todas as verificações passaram.
```

## Uso de IA

Usei IA para escrever e revisar consultas SQL e código Python. O registro de erros
encontrados e de como conferi cada resultado está em [`docs/diario_ia.md`](docs/diario_ia.md).

## Como rodar

```bash
git clone https://bitbucket.org/hiagoportela/pagamentos-recorrentes.git ou https://github.com/hiagoportela/pipeline-pagamentos-recorrentes.git
cd pagamentos-recorrentes
python -m venv venv
venv\Scripts\activate            # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

python src/generate_data.py      # gera dados sintéticos
python src/run_pipeline.py       # roda o pipeline
python src/run_queries.py        # executa as análises
python src/monitor.py            # verifica a saúde do banco
```

## Limitações conhecidas

- Dados sintéticos, com a mesma probabilidade de recusa e churn para todos os setores.
- 396 valores (1,5% das cobranças) foram estimados pela mensalidade do cliente. Isso
  assume que a cobrança sempre equivale à mensalidade; em um caso real, a regra seria
  validada com o dono do dado.
- A Selic (731 registros diários, 2024–2025) é extraída da API do Banco Central para
  demonstrar a coleta de uma terceira fonte, mas não é carregada no banco nem usada nas
  análises. Os dados de cobrança são sintéticos e não teriam relação real com os juros.
- Cobranças em quarentena podem fazer a análise de churn contar um cliente como
  cancelado antes da hora. O impacto não foi medido.
- O pipeline não tem agendador próprio. Em produção, seria orquestrado
  (por exemplo, com Airflow).

## Próximos passos

- Testes automatizados (pytest) para as funções de transformação e validação.
- Orquestração e agendamento do pipeline.
- Dashboard com as métricas de negócio.

## Tecnologias

Python (pandas, requests), SQL (SQLite), Git/Bitbucket, Github