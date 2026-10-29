"""Read-only tests of CLI formatting and exit codes; no DB connection."""
import sys
from datetime import datetime
from decimal import Decimal

import support_tool


def example_report():
    return {
        "searched_reference": "TXNTEST001",
        "matches": 1,
        "duplicate_reference": False,
        "results": [{
            "transaction": {
                "id": 1, "transaction_ref": "TXNTEST001",
                "customer_id": 2, "customer_ref": "CUST000002",
                "customer_name": "Test Customer",
                "amount": Decimal("125.50"), "status": "SUCCESS",
                "failure_code": None,
                "created_at": datetime(2026, 10, 28, 10, 0),
                "completed_at": datetime(2026, 10, 28, 10, 1),
            },
            "callbacks": [{
                "attempt_no": 1, "http_status": 200,
                "callback_status": "SUCCESS",
                "attempted_at": datetime(2026, 10, 28, 10, 1, 5),
            }],
            "flags": [],
            "recommended_actions": ["Monitor normally."],
        }],
    }


def test_human_report_has_customer_timestamps_callbacks(monkeypatch, capsys):
    monkeypatch.setattr(support_tool, "investigate", lambda reference: example_report())
    monkeypatch.setattr(sys, "argv", ["support_tool.py", "--transaction", "TXNTEST001"])
    assert support_tool.main() == 0
    output = capsys.readouterr().out
    for required in ("TXNTEST001", "CUST000002", "Test Customer",
                     "2026-10-28 10:00:00", "2026-10-28 10:01:05",
                     "125.50", "Callback Attempts: 1", "Action: Monitor normally."):
        assert required in output


def test_json_cli_serializes_datetime_and_decimal(monkeypatch, capsys):
    import json
    monkeypatch.setattr(support_tool, "investigate", lambda reference: example_report())
    monkeypatch.setattr(sys, "argv", ["support_tool.py", "--transaction", "TXNTEST001", "--json"])
    assert support_tool.main() == 0
    doc = json.loads(capsys.readouterr().out)
    assert doc["results"][0]["transaction"]["amount"] == "125.50"
    assert doc["results"][0]["transaction"]["created_at"] == "2026-10-28T10:00:00"


def test_no_match_exit_code(monkeypatch, capsys):
    monkeypatch.setattr(support_tool, "investigate",
                        lambda reference: {"searched_reference": reference, "matches": 0,
                                            "duplicate_reference": False, "results": []})
    monkeypatch.setattr(sys, "argv", ["support_tool.py", "--transaction", "MISSING"] )
    assert support_tool.main() == 2
    assert "Transaction not found" in capsys.readouterr().out
