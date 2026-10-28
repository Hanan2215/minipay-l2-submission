from datetime import datetime, timedelta

from support_tool import evaluate


NOW = datetime(2026, 10, 28, 12, 0)


def transaction(status, minutes=2, failure_code=None):
    return {
        "status": status,
        "created_at": NOW - timedelta(minutes=minutes),
        "failure_code": failure_code,
    }


def successful_callback():
    return {
        "http_status": 200,
        "callback_status": "SUCCESS",
    }


def test_stuck_processing():
    flags, _ = evaluate(transaction("PROCESSING", 30), [], NOW)
    assert "STUCK_PROCESSING" in flags


def test_success_with_callback():
    flags, _ = evaluate(
        transaction("SUCCESS"),
        [successful_callback()],
        NOW,
    )
    assert flags == []


def test_missing_success_callback():
    flags, _ = evaluate(transaction("SUCCESS"), [], NOW)
    assert "SUCCESS_CALLBACK_NOT_CONFIRMED" in flags


def test_failed_with_success_callback():
    flags, _ = evaluate(
        transaction("FAILED", failure_code="DECLINED"),
        [successful_callback()],
        NOW,
    )
    assert "FAILED_WITH_SUCCESS_CALLBACK" in flags


def test_callback_retries():
    flags, _ = evaluate(
        transaction("SUCCESS"),
        [successful_callback()] * 3,
        NOW,
    )
    assert "MULTIPLE_CALLBACK_ATTEMPTS" in flags
