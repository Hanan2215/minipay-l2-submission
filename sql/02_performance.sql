\echo '=== TRANSACTION SEARCH PERFORMANCE ==='

-- Confirm the test transaction exists
SELECT COUNT(*) AS matching_rows
FROM transactions
WHERE transaction_ref = 'TXN00040001';

-- Refresh planner statistics
ANALYZE transactions;

\echo '=== BEFORE OPTIMIZATION ==='

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, transaction_ref, status, amount, created_at
FROM transactions
WHERE transaction_ref = 'TXN00040001';

\echo '=== CREATE SEARCH INDEX ==='

CREATE INDEX IF NOT EXISTS idx_transactions_transaction_ref
ON transactions (transaction_ref);

\echo '=== AFTER OPTIMIZATION ==='

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, transaction_ref, status, amount, created_at
FROM transactions
WHERE transaction_ref = 'TXN00040001';

\echo '=== INDEX VERIFICATION ==='

SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'transactions'
ORDER BY indexname;
