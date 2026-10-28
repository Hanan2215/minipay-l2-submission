from time import perf_counter
import httpx


def test_api_health_response_time():
    start = perf_counter()

    response = httpx.get(
        "http://127.0.0.1:8000/health",
        timeout=5
    )

    elapsed = perf_counter() - start

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert elapsed < 2.0, f"Health endpoint slow: {elapsed:.3f}s"
