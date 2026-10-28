"""Isolated reproduction of intermittent MiniPay search HTTP 500.

Uses the real synthetic database in read-only mode.
Does not modify the production API or transaction data.
"""

import os
import sys
from contextlib import closing
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

DB_URL = os.getenv("MINIPAY_DATABASE_URL", "dbname=minipay")
API_KEY = os.environ["MINIPAY_API_KEY"]


def query(sql, params=()):
    with closing(
        psycopg2.connect(DB_URL, connect_timeout=5)
    ) as conn:
        conn.set_session(readonly=True)
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


unique = query("""
    SELECT transaction_ref
    FROM transactions
    GROUP BY transaction_ref
    HAVING COUNT(*) = 1
    LIMIT 1
""")[0][0]

duplicate = query("""
    SELECT transaction_ref
    FROM transactions
    GROUP BY transaction_ref
    HAVING COUNT(*) > 1
    LIMIT 1
""")[0][0]


def find_rows(reference):
    return query(
        """
        SELECT id, transaction_ref
        FROM transactions
        WHERE transaction_ref = %s
        ORDER BY id
        LIMIT 2
        """,
        (reference,),
    )


lab = FastAPI()


@lab.get("/broken/{reference}")
def broken_search(reference: str):
    rows = find_rows(reference)

    if not rows:
        raise HTTPException(404, "Not found")

    # INTENTIONALLY INJECTED DEFECT:
    # Assumes every transaction reference is unique.
    # Duplicate references cause ValueError -> HTTP 500.
    (row,) = rows

    return {"id": row[0], "transaction_ref": row[1]}


@lab.get("/fixed/{reference}")
def fixed_search(reference: str):
    rows = find_rows(reference)

    if not rows:
        raise HTTPException(404, "Not found")

    if len(rows) > 1:
        raise HTTPException(
            409, "Duplicate transaction reference"
        )

    return {
        "id": rows[0][0],
        "transaction_ref": rows[0][1],
    }


def verify(client, label, path, expected, headers=None):
    response = client.get(path, headers=headers)
    print(f"{label}: HTTP {response.status_code}")
    assert response.status_code == expected, response.text


with TestClient(lab, raise_server_exceptions=False) as client:
    print("=== INCIDENT-001: ISOLATED DEFECT REPRODUCTION ===")
    print("UNIQUE_REFERENCE:", unique)
    print("DUPLICATE_REFERENCE:", duplicate)

    verify(client, "BROKEN_UNIQUE", f"/broken/{unique}", 200)
    verify(client, "BROKEN_DUPLICATE", f"/broken/{duplicate}", 500)

    print("=== CORRECTED IMPLEMENTATION ===")
    verify(client, "FIXED_UNIQUE", f"/fixed/{unique}", 200)
    verify(client, "FIXED_DUPLICATE", f"/fixed/{duplicate}", 409)
    verify(client, "FIXED_MISSING", "/fixed/NO-SUCH-REF", 404)


from app.main import app as actual_app

with TestClient(actual_app, raise_server_exceptions=False) as client:
    headers = {"X-API-Key": API_KEY}

    print("=== EXISTING MINIPAY API REGRESSION TEST ===")

    verify(
        client, "ACTUAL_UNIQUE",
        f"/api/payments/reference/{unique}",
        200, headers
    )
    verify(
        client, "ACTUAL_DUPLICATE",
        f"/api/payments/reference/{duplicate}",
        409, headers
    )
    verify(
        client, "ACTUAL_MISSING",
        "/api/payments/reference/NO-SUCH-REF",
        404, headers
    )

print("INCIDENT-001 REPRODUCTION AND FIX VALIDATION PASSED")
