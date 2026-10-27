
-- 1. Daily transaction count and total amount by status
\echo '=== REPORT 1: DAILY STATUS SUMMARY ==='

SELECT
    created_at::date AS day,
    status,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount
FROM transactions
GROUP BY created_at::date, status
ORDER BY day, status;


-- 2. Top 10 customers by successful payment value
\echo '=== REPORT 2: TOP 10 CUSTOMERS ==='

SELECT
    c.customer_ref,
    c.name,
    COUNT(*) AS successful_transactions,
    SUM(t.amount) AS total_success_value
FROM customers c
JOIN transactions t ON t.customer_id = c.id
WHERE t.status = 'SUCCESS'
GROUP BY c.id, c.customer_ref, c.name
ORDER BY total_success_value DESC
LIMIT 10;


-- 3. Transactions stuck in processing over 15 minutes
\echo '=== REPORT 3: STUCK TRANSACTIONS ==='

SELECT
    id,
    transaction_ref,
    amount,
    status,
    created_at,
    ROUND(
        (EXTRACT(EPOCH FROM (NOW() - created_at)) / 60)::numeric,
        2
    ) AS minutes_waiting
FROM transactions
WHERE status = 'PROCESSING'
  AND created_at < NOW() - INTERVAL '15 minutes'
ORDER BY created_at, id;


-- 4. Duplicate transaction references
\echo '=== REPORT 4: DUPLICATE REFERENCES ==='

SELECT
    transaction_ref,
    COUNT(*) AS duplicate_count,
    ARRAY_AGG(id ORDER BY id) AS transaction_ids
FROM transactions
GROUP BY transaction_ref
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, transaction_ref;


-- 5. Daily payment success percentage
\echo '=== REPORT 5: DAILY SUCCESS RATE ==='

SELECT
    created_at::date AS day,
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (
        WHERE status = 'SUCCESS'
    ) AS successful_transactions,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE status = 'SUCCESS'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS success_rate_percent
FROM transactions
GROUP BY created_at::date
ORDER BY day;


-- 6. Successful transactions versus successful callbacks
\echo '=== REPORT 6: PAYMENT RECONCILIATION ==='

WITH reconciliation AS (
    SELECT
        t.id,
        t.status,
        t.amount,
        EXISTS (
            SELECT 1
            FROM callbacks cb
            WHERE cb.transaction_id = t.id
              AND cb.callback_status = 'SUCCESS'
        ) AS has_success_callback
    FROM transactions t
)
SELECT
    COUNT(*) FILTER (
        WHERE status = 'SUCCESS'
    ) AS successful_payment_count,

    COALESCE(SUM(amount) FILTER (
        WHERE status = 'SUCCESS'
    ), 0) AS successful_payment_value,

    COUNT(*) FILTER (
        WHERE has_success_callback
    ) AS callback_success_count,

    COALESCE(SUM(amount) FILTER (
        WHERE has_success_callback
    ), 0) AS callback_success_value,

    COUNT(*) FILTER (
        WHERE status = 'SUCCESS'
          AND NOT has_success_callback
    ) AS success_without_callback,

    COUNT(*) FILTER (
        WHERE status <> 'SUCCESS'
          AND has_success_callback
    ) AS callback_without_success
FROM reconciliation;


-- 7. Average and 95th percentile processing duration
\echo '=== REPORT 7: PROCESSING TIME ==='

SELECT
    COUNT(*) AS completed_transactions,

    ROUND(
        AVG(
            EXTRACT(EPOCH FROM (completed_at - created_at))
        )::numeric,
        2
    ) AS avg_processing_seconds,

    ROUND(
        (
            PERCENTILE_CONT(0.95)
            WITHIN GROUP (
                ORDER BY EXTRACT(
                    EPOCH FROM (completed_at - created_at)
                )::double precision
            )
        )::numeric,
        2
    ) AS p95_processing_seconds

FROM transactions
WHERE completed_at IS NOT NULL
  AND completed_at >= created_at;
