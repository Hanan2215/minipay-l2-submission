# Payment API Integration Notes

## Timeouts
Use separate connection and response timeouts.
A timeout does not prove a payment failed.

## Retries
Retry transient errors and timeouts with exponential backoff.
Avoid blindly retrying non-retryable validation failures.

## Idempotency
Reuse the same Idempotency-Key for retries of one payment.
The API returns the original transaction for an identical retry,
and HTTP 409 if the same key is reused with different data.

## HTTP Errors
- 400/422: Correct the request.
- 401: Check API authentication.
- 404: Requested resource was not found.
- 409: Resolve duplicate reference or idempotency conflict.
- 500/503: Investigate server or dependency issues.

## Response Time
The automated health test uses a 2-second threshold
on the local assessment environment.

## Run API Tests
.venv/bin/python -m pytest tests/api/ -v
