-- Sales performance metrics (PostgreSQL syntax)
-- Source tables mirror the CSVs in data/raw/:
--   orders(order_id, month, region, category, channel, rep, quantity, revenue, gross_profit, new_customer)
--   targets(month, target)
-- `month` is stored as text 'YYYY-MM'.

-- 1. Monthly revenue vs target, with attainment and margin
SELECT
    o.month,
    ROUND(SUM(o.revenue))                                   AS revenue,
    t.target,
    ROUND(100.0 * SUM(o.revenue) / t.target, 1)             AS attainment_pct,
    ROUND(100.0 * SUM(o.gross_profit) / SUM(o.revenue), 1)  AS margin_pct,
    COUNT(*)                                                AS orders,
    ROUND(SUM(o.revenue) / COUNT(*), 1)                     AS avg_order_value,
    SUM(o.new_customer)                                     AS new_customers
FROM orders o
JOIN targets t USING (month)
GROUP BY o.month, t.target
ORDER BY o.month;

-- 2. Running (year-to-date style) revenue vs target with window functions
WITH m AS (
    SELECT o.month, SUM(o.revenue) AS revenue, t.target
    FROM orders o JOIN targets t USING (month)
    GROUP BY o.month, t.target
)
SELECT
    month,
    ROUND(SUM(revenue) OVER (ORDER BY month)) AS cumulative_revenue,
    ROUND(SUM(target)  OVER (ORDER BY month)) AS cumulative_target,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY month) / SUM(target) OVER (ORDER BY month), 1) AS cumulative_attainment_pct
FROM m
ORDER BY month;

-- 3. Revenue and margin by region / product line / channel (swap the GROUP BY column)
SELECT
    region,
    ROUND(SUM(revenue))                                        AS revenue,
    ROUND(SUM(gross_profit))                                   AS gross_profit,
    COUNT(*)                                                   AS orders,
    ROUND(100.0 * SUM(gross_profit) / SUM(revenue), 1)         AS margin_pct,
    ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS share_pct
FROM orders
GROUP BY region
ORDER BY revenue DESC;

-- 4. Product lines ranked by margin, with revenue rank for comparison
SELECT
    category,
    ROUND(SUM(revenue))                                     AS revenue,
    ROUND(100.0 * SUM(gross_profit) / SUM(revenue), 1)      AS margin_pct,
    RANK() OVER (ORDER BY SUM(revenue) DESC)                AS revenue_rank,
    RANK() OVER (ORDER BY SUM(gross_profit) / SUM(revenue) DESC) AS margin_rank
FROM orders
GROUP BY category
ORDER BY margin_rank;

-- 5. Months on target
SELECT COUNT(*) AS months_on_target
FROM (
    SELECT o.month
    FROM orders o JOIN targets t USING (month)
    GROUP BY o.month, t.target
    HAVING SUM(o.revenue) >= t.target
) hit;
