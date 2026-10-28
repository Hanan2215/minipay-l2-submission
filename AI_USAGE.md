# AI Usage Disclosure

## Tool Used
OpenAI ChatGPT.

## Work Supported by AI
- Linux and Git command guidance
- PostgreSQL reporting and optimization
- FastAPI design and troubleshooting
- Python investigation utility
- Pytest and Playwright automation
- Container and Kubernetes configuration
- Incident RCA documentation

## Representative Interactions
1. Generate SQL investigation queries for MiniPay transactions.
2. Implement FastAPI payment endpoints with idempotency.
3. Write unit tests for transaction support classifications.
4. Diagnose the container startup PermissionError.
5. Explain Kubernetes selector, port and probe defects.

## Validation
AI output was not treated as proof of correctness.

The candidate executed local PostgreSQL queries, API tests,
Python unit tests, browser automation, container smoke tests,
and Kubernetes static validation.

Evidence is preserved under evidence/.

## Corrections to AI-Generated Work
The first container image built successfully but crashed with
PermissionError reading app/main.py as the non-root user.

Container logs exposed the defect. Dockerfile ownership
was corrected, image rebuilt, and API/UI returned HTTP 200.

The Web UI route was also initially missing. It was added
after browser HTTP 404 and file/route checks identified
the missing implementation.

These problems were resolved using actual execution evidence.

## Engineering Ownership
The submitted code and generated guidance must be understood,
verified and explainable during the technical interview.
