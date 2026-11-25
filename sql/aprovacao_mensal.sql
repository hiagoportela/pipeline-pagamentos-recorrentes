-- Qual a taxa de aprovação das cobranças a cada mês?
SELECT
    strftime('%Y-%m', data_cobranca) AS mes,
    COUNT(*) AS total_cobrancas,
    SUM(CASE WHEN status = 'aprovada' THEN 1 ELSE 0 END) AS aprovadas,
    ROUND(100.0 * SUM(CASE WHEN status = 'aprovada' THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_aprovacao_pct
FROM cobrancas
GROUP BY mes
ORDER BY mes;