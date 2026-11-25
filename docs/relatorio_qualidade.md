# Relatório de Qualidade de Dados

| Regra | Antes | Depois |
|---|---|---|
| valor_nulo | 266 | 0 |
| valor_zero_ou_negativo | 133 | 0 |
| id_duplicado | 132 | 0 |
| data_futura | 79 | 0 |
| status_invalido | 0 | 0 |
| cliente_inexistente | 0 | 0 |

## Ações de tratamento

- linhas de entrada: 26620
- duplicatas removidas: 132
- linhas enviadas para quarentena (data futura): 79
- valores recuperados pela mensalidade do cliente: 396
- linhas de saída: 26409