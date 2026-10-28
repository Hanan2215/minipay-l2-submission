import os
import uuid
import httpx

BASE = "http://minipay-api.minipay.svc.cluster.local"
KEY = os.environ["MINIPAY_API_KEY"]

def check(label, response, expected):
    print(f"{label}: HTTP {response.status_code}", flush=True)
    assert response.status_code == expected, response.text

with httpx.Client(base_url=BASE, timeout=10) as client:
    r = client.get("/health")
    check("K8S_SERVICE_HEALTH", r, 200)
    assert r.json()["database"] == "connected"

    check("K8S_WEB_UI", client.get("/ui/"), 200)
    check("K8S_AUTH", client.get("/api/payments/1"), 401)

    auth = {"X-API-Key": KEY}

    r = client.post("/api/customers", headers=auth, json={
        "customer_ref": "K8S-" + uuid.uuid4().hex[:16],
        "name": "Kubernetes QA Customer"
    })
    check("K8S_CREATE_CUSTOMER", r, 201)
    customer_id = r.json()["id"]

    headers = {
        **auth,
        "Idempotency-Key": uuid.uuid4().hex
    }
    data = {"customer_id": customer_id, "amount": "125.50"}

    r = client.post("/api/payments", headers=headers, json=data)
    check("K8S_CREATE_PAYMENT", r, 201)
    payment_id = r.json()["id"]

    r = client.post("/api/payments", headers=headers, json=data)
    check("K8S_IDEMPOTENT_RETRY", r, 200)
    assert r.json()["id"] == payment_id

    r = client.get(f"/api/payments/{payment_id}", headers=auth)
    check("K8S_PAYMENT_LOOKUP", r, 200)
    assert any(
        c["callback_status"] == "SUCCESS"
        for c in r.json()["callbacks"]
    )

    r = client.get(
        f"/api/customers/{customer_id}/payments",
        headers=auth
    )
    check("K8S_CUSTOMER_HISTORY", r, 200)
    assert any(p["id"] == payment_id for p in r.json()["payments"])

print("KUBERNETES LIVE SERVICE TESTS PASSED")
