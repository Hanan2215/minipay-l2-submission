# MiniPay Python L2 Support Tool

The working CLI is located at ../support_tool.py.

Run from the repository root:

.venv/bin/python support_tool.py --transaction TXN00000001

JSON output:

.venv/bin/python support_tool.py --transaction TXN00000001 --json

The utility performs read-only PostgreSQL investigation.
Unit tests are located in tests/unit/.


The default human-readable report includes customer identity/ref,
transaction reference, amount/status, creation/completion timestamps,
callback attempts/timestamps, anomaly flags and next actions.
Use `--verbose` to emit non-secret operational status messages to
stderr. Exit codes: `0` = found; `2` = no matching transaction;
`3` = database error; invalid CLI input uses argparse's exit code 2.

The tool performs database reads only; avoid investigating live client
data without authorization. The local PostgreSQL database from the
seeded assessment is separate from the K3s demo database.
