import hashlib
import logging
import os
import secrets
import uuid
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("minipay")

API_KEY = os.getenv("MINIPAY_API_KEY")
DB_URL = os.getenv("MINIPAY_DATABASE_URL", "dbname=minipay")

if not API_KEY:
    raise RuntimeError("MINIPAY_API_KEY is required")

app = FastAPI(title="MiniPay API", version="1.0.0")


@contextmanager
def database():
    try:
        conn = psycopg2.connect(DB_URL, connect_timeout=5)
    except psycopg2.OperationalError:
        log.exception("Database connection failed")
        raise HTTPException(503, "Database unavailable")

    try:
        with conn:
            yield conn
    finally:
        conn.close()


def serialize(row):
    return {
        k: (
            v.isoformat() if isinstance(v, datetime)
            else str(v) if isinstance(v, Decimal)
            else v
        )
        for k, v in dict(row).items()
    }


def authenticate(x_api_key: str | None = Header(default=None)):
    if not x_api_key or not secrets.compare_digest(
        x_api_key, API_KEY
    ):
        raise HTTPException(401, "Invalid or missing API key")


class CustomerIn(BaseModel):
    customer_ref: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=120)


class PaymentIn(BaseModel):
    customer_id: int = Field(gt=0)
    amount: Decimal = Field(
        gt=0, max_digits=14, decimal_places=2
    )


@app.get("/health")
def health():
    with database() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
    return {"status": "healthy", "database": "connected"}


@app.post("/api/customers", dependencies=[Depends(authenticate)])
def create_customer(payload: CustomerIn):
    with database() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO customers (customer_ref, name)
                VALUES (%s, %s)
                ON CONFLICT (customer_ref) DO NOTHING
                RETURNING id, customer_ref, name
                """,
                (payload.customer_ref, payload.name),
            )
            row = cur.fetchone()

            if row is None:
                raise HTTPException(409, "Customer reference exists")

    return JSONResponse(status_code=201, content=serialize(row))


@app.post("/api/payments", dependencies=[Depends(authenticate)])
def create_payment(
    payload: PaymentIn,
    idempotency_key: str | None = Header(
        default=None, alias="Idempotency-Key"
    ),
):
    if not idempotency_key or len(idempotency_key) > 128:
        raise HTTPException(
            400, "Valid Idempotency-Key header required"
        )

    fingerprint = hashlib.sha256(
        f"{payload.customer_id}:{payload.amount:.2f}".encode()
    ).hexdigest()

    with database() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Serialize requests with the same idempotency key.
            cur.execute(
                "SELECT pg_advisory_xact_lock(hashtext(%s))",
                (idempotency_key,),
            )

            cur.execute(
                """
                SELECT fingerprint, transaction_id
                FROM payment_requests
                WHERE idempotency_key = %s
                """,
                (idempotency_key,),
            )
            existing = cur.fetchone()

            if existing:
                if existing["fingerprint"] != fingerprint:
                    raise HTTPException(
                        409, "Idempotency key reused with different data"
                    )

                cur.execute(
                    """
                    SELECT id, transaction_ref, customer_id,
                           amount, status, created_at, completed_at
                    FROM transactions WHERE id = %s
                    """,
                    (existing["transaction_id"],),
                )
                return JSONResponse(
                    status_code=200,
                    content=serialize(cur.fetchone()),
                )

            cur.execute(
                "SELECT id FROM customers WHERE id = %s",
                (payload.customer_id,),
            )
            if not cur.fetchone():
                raise HTTPException(404, "Customer not found")

            # Simulated provider success; no actual funds move.
            ref = "DEMO-" + uuid.uuid4().hex[:20].upper()

            cur.execute(
                """
                INSERT INTO transactions
                (transaction_ref, customer_id, amount,
                 status, created_at, completed_at)
                VALUES (%s, %s, %s, 'SUCCESS', NOW(), NOW())
                RETURNING id, transaction_ref, customer_id,
                          amount, status, created_at, completed_at
                """,
                (ref, payload.customer_id, payload.amount),
            )
            payment = cur.fetchone()

            cur.execute(
                """
                INSERT INTO callbacks
                (transaction_id, attempt_no, http_status,
                 callback_status, attempted_at)
                VALUES (%s, 1, 200, 'SUCCESS', NOW())
                """,
                (payment["id"],),
            )

            cur.execute(
                """
                INSERT INTO payment_requests
                (idempotency_key, fingerprint, transaction_id)
                VALUES (%s, %s, %s)
                """,
                (idempotency_key, fingerprint, payment["id"]),
            )

    return JSONResponse(
        status_code=201, content=serialize(payment)
    )


@app.get("/api/payments/reference/{reference}",
         dependencies=[Depends(authenticate)])
def find_payment_by_reference(reference: str):
    with database() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, transaction_ref, customer_id,
                       amount, status, failure_code,
                       created_at, completed_at
                FROM transactions
                WHERE transaction_ref = %s
                ORDER BY id
                LIMIT 2
                """,
                (reference,),
            )
            rows = cur.fetchall()

    if not rows:
        raise HTTPException(404, "Transaction not found")

    if len(rows) > 1:
        raise HTTPException(
            409, "Duplicate reference; investigate using transaction ID"
        )

    return serialize(rows[0])


@app.get("/api/payments/{payment_id}",
         dependencies=[Depends(authenticate)])
def get_payment(payment_id: int):
    with database() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, transaction_ref, customer_id,
                       amount, status, failure_code,
                       created_at, completed_at
                FROM transactions WHERE id = %s
                """,
                (payment_id,),
            )
            payment = cur.fetchone()

            if not payment:
                raise HTTPException(404, "Payment not found")

            cur.execute(
                """
                SELECT attempt_no, http_status,
                       callback_status, attempted_at
                FROM callbacks WHERE transaction_id = %s
                ORDER BY attempt_no
                """,
                (payment_id,),
            )
            callbacks = cur.fetchall()

    result = serialize(payment)
    result["callbacks"] = [serialize(c) for c in callbacks]
    return result


@app.get("/api/customers/{customer_id}/payments",
         dependencies=[Depends(authenticate)])
def customer_payments(customer_id: int):
    with database() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id FROM customers WHERE id = %s",
                (customer_id,),
            )
            if not cur.fetchone():
                raise HTTPException(404, "Customer not found")

            cur.execute(
                """
                SELECT id, transaction_ref, amount,
                       status, created_at, completed_at
                FROM transactions
                WHERE customer_id = %s
                ORDER BY created_at DESC, id DESC
                LIMIT 100
                """,
                (customer_id,),
            )
            rows = cur.fetchall()

    return {"customer_id": customer_id,
            "payments": [serialize(r) for r in rows]}


from pathlib import Path
from fastapi.staticfiles import StaticFiles

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
app.mount("/ui", StaticFiles(directory=str(WEB_DIR), html=True), name="ui")
