-- Qual setor tem mais cobranças recusadas e quanto dinheiro isso representa?
SELECT
    c.setor,
    COUNT(*) AS total_cobrancas,
    SUM(CASE WHEN b.status = 'recusada' THEN 1 ELSE 0 END) AS recusadas,
    ROUND(100.0 * SUM(CASE WHEN b.status = 'recusada' THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_recusa_pct,
    ROUND(SUM(CASE WHEN b.status = 'recusada' THEN b.valor ELSE 0 END), 2) AS valor_recusado
FROM cobrancas b
JOIN clientes c ON c.cliente_id = b.cliente_id
GROUP BY c.setor
ORDER BY taxa_recusa_pct DESC;