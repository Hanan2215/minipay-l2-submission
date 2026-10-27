# MiniPay SQL Performance Investigation

## Objective

Investigate and optimize transaction lookup performance
using PostgreSQL and 50,000 synthetic transactions.

## Environment

- Database: PostgreSQL 15
- Customers: 1,000
- Transactions: 50,000
- Callbacks: 56,589

## Problem

Transaction searches using transaction_ref were
performing a sequential scan because the supplied
schema had no index on transaction_ref.

## Query Tested

SELECT id, transaction_ref, status, amount, created_at
FROM transactions
WHERE transaction_ref = 'TXN00040001';

## Before Optimization

Execution plan: Sequential Scan
Execution time: 3.119 ms

The database scanned the transactions table
to locate the matching reference.

## Optimization

Created a non-unique B-tree index:

CREATE INDEX IF NOT EXISTS
idx_transactions_transaction_ref
ON transactions (transaction_ref);

A non-unique index was selected because the
provided synthetic dataset intentionally contains
duplicate transaction references.

No transaction source records were modified.

## After Optimization

Execution plan: Index Scan
Execution time: 0.051 ms

## Results

Before: 3.119 ms
After: 0.051 ms
Measured speedup: approximately 61.2x
Measured latency reduction: approximately 98.4%

These results represent one before/after measurement
on the local synthetic dataset.

Execution time may vary because of caching,
system load, query planning and dataset size.

## Evidence

Full EXPLAIN ANALYZE output:
evidence/sql-performance.txt

SQL test:
sql/02_performance.sql

## Reproducibility

Run the performance script against a freshly seeded
database that does not already contain the index.

The current database already has the index.
Re-running the script will not reproduce the
original unindexed baseline.

Do not delete production indexes or source
data merely to repeat the experiment.

## Production Considerations

- Validate improvements with repeated measurements.
- Consider write overhead and index storage costs.
- Use CREATE INDEX CONCURRENTLY where appropriate
  for an active PostgreSQL production workload.
- Monitor actual query plans as data volume grows.

## Conclusion

Indexing transaction_ref improved the measured
transaction lookup performance while preserving
the original transaction records.
