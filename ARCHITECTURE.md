# MiniPay Architecture

## Components

Browser UI
    |
    v
FastAPI REST Service
    |
    v
PostgreSQL Database

The application also includes a read-only Python L2
transaction investigation CLI.

## API
- POST /api/customers
- POST /api/payments
- GET /api/payments/{id}
- GET /api/payments/reference/{reference}
- GET /api/customers/{id}/payments
- GET /health

## Security
Protected API operations require X-API-Key.
Secrets are loaded from environment configuration.

## Payment Safety
This is a simulated payment system. No real funds move.

Payment requests use an Idempotency-Key and a separate
payment_requests table to prevent duplicate creation
when clients retry the same operation.

Existing transaction references are not guaranteed unique.
Ambiguous references return HTTP 409.

## Database
customers, transactions, callbacks and payment_requests.

## Deployment
A Docker-compatible image runs the FastAPI application.
Kubernetes manifests describe API replicas, PostgreSQL
StatefulSet, services, configuration, probes and storage.

## Operational Evidence
See evidence/, investigation/ and sql/PERFORMANCE.md.
