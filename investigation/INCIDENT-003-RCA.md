# INCIDENT-003 — Transaction Search Performance

Priority: P2
Status: Local optimization verified.

## Problem
Transaction-reference searches become less efficient as
transaction volume increases.

## Test Environment
PostgreSQL 15, local virtual machine.
Initial synthetic dataset: 50,000 transactions and
56,589 callback attempts.

## Investigation and Root Cause
EXPLAIN ANALYZE initially showed a sequential scan when
looking up transactions by transaction_ref.

The tested query lacked a suitable lookup index.

## Corrective Action
Created a non-unique B-tree index named
idx_transactions_transaction_ref on
transactions(transaction_ref).

A non-unique index was used because duplicate references
exist in the synthetic data.

## Before and After Evidence
Before: Sequential Scan, 3.119 ms.
After: Index Scan, 0.051 ms.
Observed improvement: approximately 61.2x.

Evidence:
evidence/sql-performance.txt
sql/02_performance.sql
sql/PERFORMANCE.md

## Validation and Limitations
The query plan changed from Seq Scan to Index Scan.
The result is one local measurement, not a production
performance guarantee.

## Prevention
Monitor slow queries, periodically review execution plans,
maintain database statistics, and benchmark with
representative workloads.
