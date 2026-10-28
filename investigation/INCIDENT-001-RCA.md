# INCIDENT-001 — Intermittent Transaction Search HTTP 500

Priority: P2
Status: Isolated reproduction and correction verified.

## Observations
Some transaction searches succeed while others return HTTP 500.
The synthetic database contains duplicate transaction references.

## Reproduction
An isolated test deliberately introduced a defect that assumes
each transaction reference matches exactly one database row.

Evidence: evidence/incident001-reproduction.txt

Broken unique reference: HTTP 200
Broken duplicate reference: HTTP 500

## Root Cause
Unsafe single-row unpacking raises ValueError when a transaction
reference matches multiple database records.

This is a deliberately simulated defect, not a confirmed
production root cause.

## Hypotheses Considered
Database outage, authentication failure and duplicate-reference
handling. The isolated test confirmed the duplicate-reference
handling defect.

## Immediate Correction
Check the number of matching records.
Return HTTP 404 when missing and HTTP 409 when duplicates exist.

## Validation
Corrected unique reference: HTTP 200
Corrected duplicate reference: HTTP 409
Corrected missing reference: HTTP 404

The existing MiniPay API independently passed the same three
regression checks without modification.

## Preventive Actions
Add regression tests for duplicate references, use unique
transaction IDs for investigations, monitor HTTP 500 errors,
and review database uniqueness requirements.

No existing transaction records were modified.
