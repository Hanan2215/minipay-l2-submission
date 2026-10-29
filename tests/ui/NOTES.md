# MiniPay UI Automation — Test Scope and CI Strategy

## Existing browser test

`tests/ui/test_ui.py` uses Playwright Chromium with stable element IDs
(e.g. `#reference`, `#searchBtn`, `#payBtn`) and Playwright assertions.
It covers:

1. Open `/ui/` and enter the API key (the app has API-key entry, not a
   separate login screen).
2. Search for an existing transaction reference `TXN00000001`.
3. Search for a nonexistent transaction and assert HTTP 404.
4. Submit a synthetic demo payment and assert HTTP 201 / SUCCESS.
5. Save evidence screenshots on completion.

The test assumes the local API is running on port `8000`, a valid
`MINIPAY_API_KEY` in `.env`, and a seeded local database containing
`TXN00000001` and customer ID `1`. It creates a synthetic payment;
therefore run it only against an isolated **test** database.

## Run

```bash
.venv/bin/python -m playwright install chromium
.venv/bin/python -m pytest tests/ui/ -v
```

Previously captured result: `evidence/ui-tests.txt` (1/1 PASS);
screenshots: `evidence/ui-search-success.png`,
`evidence/ui-search-not-found.png`, `evidence/ui-payment-success.png`.

## Recommended CI Integration (plan; not claimed implemented)

- Provision a fresh PostgreSQL service with disposable test data.
- Install pinned Python dependencies and Playwright Chromium.
- Seed deterministic fixtures; start the API and wait for `/health`.
- Run API unit/integration tests first; run the short browser smoke
  journey on each pull request and release candidate.
- Run a broader regression suite (browser permutations, failed
  callbacks, duplicate references, timeouts, data cleanup) nightly
  or before significant releases.
- Publish test output and screenshots as CI artifacts; never expose
  API keys in logs.

No `.github/workflows` file or live CI run is claimed here.
