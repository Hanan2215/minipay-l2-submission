import os
import uuid

import httpx
import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="module")
def api():
    load_dotenv(".env")
    key = os.environ["MINIPAY_API_KEY"]

    with httpx.Client(
        base_url="http://127.0.0.1:8000",
        timeout=10
    ) as client:
        yield client, {"X-API-Key": key}


def test_health(api):
    client, _ = api
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_authentication(api):
    client, _ = api

    assert client.get("/api/payments/1").status_code == 401

    r = client.get(
        "/api/payments/1",
        headers={"X-API-Key": "invalid"}
    )
    assert r.status_code == 401


def test_customer_payment_workflow(api):
    client, auth = api

    ref = "QA-" + uuid.uuid4().hex[:20]
    customer_data = {
        "customer_ref": ref,
        "name": "Automated Test Customer"
    }

    r = client.post(
        "/api/customers",
        json=customer_data,
        headers=auth
    )
    assert r.status_code == 201, r.text
    customer_id = r.json()["id"]

    duplicate_customer = client.post(
        "/api/customers",
        json=customer_data,
        headers=auth
    )
    assert duplicate_customer.status_code == 409

    headers = {
        **auth,
        "Idempotency-Key": uuid.uuid4().hex
    }

    payment_data = {
        "customer_id": customer_id,
        "amount": "125.50"
    }

    first = client.post(
        "/api/payments",
        json=payment_data,
        headers=headers
    )
    assert first.status_code == 201, first.text

    payment = first.json()
    payment_id = payment["id"]

    retry = client.post(
        "/api/payments",
        json=payment_data,
        headers=headers
    )
    assert retry.status_code == 200
    assert retry.json()["id"] == payment_id

    conflict = client.post(
        "/api/payments",
        json={
            "customer_id": customer_id,
            "amount": "999.00"
        },
        headers=headers
    )
    assert conflict.status_code == 409

    detail = client.get(
        f"/api/payments/{payment_id}",
        headers=auth
    )
    assert detail.status_code == 200
    assert detail.json()["callbacks"][0]["callback_status"] == "SUCCESS"

    search = client.get(
        f"/api/payments/reference/{payment['transaction_ref']}",
        headers=auth
    )
    assert search.status_code == 200
    assert search.json()["id"] == payment_id

    history = client.get(
        f"/api/customers/{customer_id}/payments",
        headers=auth
    )
    assert history.status_code == 200
    assert any(
        p["id"] == payment_id
        for p in history.json()["payments"]
    )


def test_error_handling(api):
    client, auth = api

    missing = client.get(
        "/api/payments/999999999",
        headers=auth
    )
    assert missing.status_code == 404

    invalid = client.post(
        "/api/payments",
        json={"customer_id": 1, "amount": "-5"},
        headers={
            **auth,
            "Idempotency-Key": uuid.uuid4().hex
        }
    )
    assert invalid.status_code == 422

    no_key = client.post(
        "/api/payments",
        json={"customer_id": 1, "amount": "10.00"},
        headers=auth
    )
    assert no_key.status_code == 400
