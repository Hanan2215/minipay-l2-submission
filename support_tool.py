#!/usr/bin/env python3
"""Read-only MiniPay transaction investigation tool."""

import argparse
import json
import logging
import os
import sys
from contextlib import closing
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

logger = logging.getLogger("minipay.support_tool")


def evaluate(transaction, callbacks, now):
    flags = []
    actions = []
    status = str(transaction["status"]).upper()

    callback_ok = any(
        str(cb["callback_status"]).upper() in ("SUCCESS", "DELIVERED")
        and cb["http_status"] is not None
        and 200 <= cb["http_status"] < 300
        for cb in callbacks
    )

    created = transaction["created_at"]

    if (
        status == "PROCESSING"
        and created
        and created < now - timedelta(minutes=15)
    ):
        flags.append("STUCK_PROCESSING")
        actions.append("Check payment processor and transaction timeout.")

    if status == "SUCCESS" and not callback_ok:
        flags.append("SUCCESS_CALLBACK_NOT_CONFIRMED")
        actions.append("Check callback delivery and retry history.")

    if status == "FAILED" and callback_ok:
        flags.append("FAILED_WITH_SUCCESS_CALLBACK")
        actions.append("Investigate payment/callback status mismatch.")

    if status == "FAILED" and not transaction.get("failure_code"):
        flags.append("MISSING_FAILURE_CODE")
        actions.append("Review failure logs for the reason code.")

    if len(callbacks) >= 3:
        flags.append("MULTIPLE_CALLBACK_ATTEMPTS")
        actions.append("Review callback errors and retry policy.")

    if not actions:
        actions.append("No immediate anomaly detected; monitor normally.")

    return flags, actions


def json_value(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Unsupported type: {type(obj).__name__}")


def investigate(reference):
    load_dotenv(Path(__file__).resolve().parent / ".env")
    db_url = os.getenv("MINIPAY_DATABASE_URL", "dbname=minipay")

    with closing(psycopg2.connect(db_url, connect_timeout=5)) as conn:
        conn.set_session(readonly=True)

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT CURRENT_TIMESTAMP::timestamp AS db_now")
            now = cur.fetchone()["db_now"]

            cur.execute(
                """
                SELECT t.id, t.transaction_ref, t.customer_id,
                       c.customer_ref, c.name AS customer_name,
                       t.amount, t.status, t.failure_code,
                       t.created_at, t.completed_at
                FROM transactions t
                LEFT JOIN customers c ON c.id = t.customer_id
                WHERE t.transaction_ref = %s
                ORDER BY t.id
                """,
                (reference,),
            )
            transactions = [dict(row) for row in cur.fetchall()]

            callbacks_by_id = {t["id"]: [] for t in transactions}

            if transactions:
                ids = [t["id"] for t in transactions]

                cur.execute(
                    """
                    SELECT transaction_id, attempt_no,
                           http_status, callback_status, attempted_at
                    FROM callbacks
                    WHERE transaction_id = ANY(%s)
                    ORDER BY transaction_id, attempt_no
                    """,
                    (ids,),
                )

                for cb in cur.fetchall():
                    callbacks_by_id[cb["transaction_id"]].append(
                        dict(cb)
                    )

    results = []

    for transaction in transactions:
        callbacks = callbacks_by_id[transaction["id"]]
        flags, actions = evaluate(transaction, callbacks, now)

        results.append({
            "transaction": transaction,
            "callbacks": callbacks,
            "flags": flags,
            "recommended_actions": actions,
        })

    return {
        "searched_reference": reference,
        "matches": len(results),
        "duplicate_reference": len(results) > 1,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Read-only MiniPay L2 transaction investigation"
    )
    parser.add_argument("--transaction", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true", help="Show operational messages on stderr")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    reference = args.transaction.strip()
    if not reference:
        parser.error("Transaction reference cannot be empty")

    try:
        report = investigate(reference)
    except psycopg2.Error as exc:
        logger.error(
            "Database investigation failed (SQLSTATE: %s)",
            exc.pgcode or "connection",
        )
        return 3

    logger.info("Investigation complete: matches=%s, duplicates=%s",
                report["matches"], report["duplicate_reference"])

    if args.json:
        print(json.dumps(report, indent=2, default=json_value))
    else:
        print("=== MINIPAY L2 INVESTIGATION ===")
        print("Reference:", reference)
        print("Matches:", report["matches"])

        if report["duplicate_reference"]:
            print("WARNING: DUPLICATE TRANSACTION REFERENCE")
            print("Investigate each transaction using its unique ID.")

        for item in report["results"]:
            t = item["transaction"]
            print(f"\nTransaction ID: {t['id']}")
            print("Transaction Reference:", t["transaction_ref"])
            print("Customer ID:", t["customer_id"])
            print("Customer Reference:", t.get("customer_ref") or "N/A")
            print("Customer Name:", t.get("customer_name") or "N/A")
            print("Amount:", t["amount"])
            print("Status:", t["status"])
            print("Failure Code:", t["failure_code"])
            print("Created At:", t.get("created_at") or "N/A")
            print("Completed At:", t.get("completed_at") or "N/A")
            print("Callback Attempts:", len(item["callbacks"]))

            for cb in item["callbacks"]:
                print(
                    f"  Attempt {cb['attempt_no']}: "
                    f"HTTP {cb['http_status']} / "
                    f"{cb['callback_status']} / "
                    f"At {cb.get('attempted_at') or 'N/A'}"
                )

            print("Flags:", ", ".join(item["flags"]) or "NONE")
            for action in item["recommended_actions"]:
                print("Action:", action)

        if not report["matches"]:
            print("Transaction not found")

    return 0 if report["matches"] else 2


if __name__ == "__main__":
    sys.exit(main())
