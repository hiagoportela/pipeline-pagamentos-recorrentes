-- Qual a receita recorrente aprovada por mês e quanto variou em relação ao mês anterior?
WITH receita AS (
    SELECT strftime('%Y-%m', data_cobranca) AS mes,
           ROUND(SUM(valor), 2) AS receita_aprovada
    FROM cobrancas
    WHERE status = 'aprovada'
    GROUP BY mes
)
SELECT
    mes,
    receita_aprovada,
    LAG(receita_aprovada) OVER (ORDER BY mes) AS mes_anterior,
    ROUND(100.0 * (receita_aprovada - LAG(receita_aprovada) OVER (ORDER BY mes))
          / LAG(receita_aprovada) OVER (ORDER BY mes), 2) AS variacao_pct
FROM receita
ORDER BY mes;