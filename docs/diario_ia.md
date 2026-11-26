# Diário de Uso de IA

Registro de como ferramentas de IA foram utilizadas no desenvolvimento deste projeto, problemas identificados nas sugestões e métodos usados para validar os resultados.

## Onde a IA foi utilizada

* **Geração de dados sintéticos (`src/generate_data.py`):** criação da lógica de geração de clientes, cobranças e injeção controlada de anomalias (nulos, duplicatas e datas futuras).
* **Consultas analíticas (`sql/`):** estruturação de CTEs e *window functions* (`LAG`) para cálculo de churn e variação mensal de receita.
* **Revisão e refatoração (`src/`):** organização das etapas de extração, validação e carga em módulos separados.

---

## Erros identificados e correções aplicadas

### 1. Falsos positivos no cálculo de churn (`sql/churn_mensal.sql`)
* **O que a IA sugeriu:** considerar qualquer cliente sem cobrança aprovada no mês como cancelado.
* **Problema encontrado:** clientes que tiveram cobrança recusada ou enviada para quarentena estavam sendo contados indevidamente como churn.
* **Correção:** ajuste na query para diferenciar status de cancelamento explícito de falhas pontuais de pagamento.

### 2. Tratamento de falha na API da Selic (`src/extract.py`)
* **O que a IA sugeriu:** interromper o pipeline com exceção caso a requisição HTTP retornasse erro.
* **Problema encontrado:** durante os testes reais, a API do Banco Central retornou erro `406`, o que derrubaria toda a carga de clientes e cobranças.
* **Correção:** isolamento da falha da API com registro de aviso (*warning*), permitindo que o fluxo principal seguisse sem bloqueio.

### 3. Regra de recuperação de valores inválidos (`src/transform.py`)
* **O que a IA sugeriu:** descartar linhas com valor nulo ou menor/igual a zero.
* **Problema encontrado:** o descarte direto reduzia a base de cobranças sem necessidade, já que o cadastro do cliente possui o valor da mensalidade contratada.
* **Correção:** substituição do valor inválido pela mensalidade do cliente (recuperando 396 registros) e documentação dessa premissa no relatório de qualidade.

---

## Como os resultados foram conferidos

* **Conferência contra parâmetros do gerador:** comparação das taxas obtidas no SQL (aprovação entre 81,7% e 88,2%; recusa entre 9,6% e 9,8%) com as probabilidades configuradas no script `src/generate_data.py` (85% de aprovação).
* **Reconciliação linha a linha:** validação matemática entre entrada, duplicatas removidas, registros em quarentena e linhas carregadas no SQLite (`26.620 - 132 - 79 = 26.409`).
* **Testes de injeção de falha (`src/simular_falha.py`):** inserção proposital de nulos e registros órfãos no banco para confirmar se `src/monitor.py` detectava os problemas e retornava código de saída `1`. 