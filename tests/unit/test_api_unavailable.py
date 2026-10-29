"""Prove dependency failure maps to HTTP 503 without touching a live database."""
import importlib


def test_database_unavailable_returns_503(monkeypatch):
    monkeypatch.setenv("MINIPAY_API_KEY", "local-test-only-not-a-secret")
    api = importlib.import_module("app.main")
    from fastapi.testclient import TestClient

    def no_database(*_args, **_kwargs):
        raise api.psycopg2.OperationalError("simulated database outage")

    monkeypatch.setattr(api.psycopg2, "connect", no_database)
    response = TestClient(api.app).get("/health")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
