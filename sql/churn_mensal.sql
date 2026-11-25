-- Quantos clientes ativos e quantos cancelaram em cada mês?
WITH ultima AS (
    SELECT cliente_id, MAX(strftime('%Y-%m', data_cobranca)) AS ultimo_mes
    FROM cobrancas
    GROUP BY cliente_id
),
ativos AS (
    SELECT strftime('%Y-%m', data_cobranca) AS mes,
           COUNT(DISTINCT cliente_id) AS clientes_ativos
    FROM cobrancas
    GROUP BY mes
),
cancelados AS (
    SELECT ultimo_mes AS mes, COUNT(*) AS clientes_cancelados
    FROM ultima
    WHERE ultimo_mes < '2025-12'
    GROUP BY ultimo_mes
)
SELECT
    a.mes,
    a.clientes_ativos,
    COALESCE(c.clientes_cancelados, 0) AS clientes_cancelados,
    ROUND(100.0 * COALESCE(c.clientes_cancelados, 0) / a.clientes_ativos, 2) AS churn_pct
FROM ativos a
LEFT JOIN cancelados c ON c.mes = a.mes
ORDER BY a.mes;