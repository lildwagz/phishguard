"""Hardening checks from plans/2026-11-12-keamanan-api.md."""
import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.security import FixedWindowLimiter

client = TestClient(main.app)
OK_TEXT = "Nanti sore jadi kumpul kelompok di perpustakaan jam 4 ya"


@pytest.fixture
def small_limit(monkeypatch):
    monkeypatch.setattr(main, "limiter", FixedWindowLimiter(3))


def test_rate_limit_returns_429_with_retry_after(small_limit):
    codes = [client.post("/v1/predict", json={"text": OK_TEXT}).status_code for _ in range(5)]
    assert codes == [200, 200, 200, 429, 429]
    r = client.post("/v1/predict", json={"text": OK_TEXT})
    assert 1 <= int(r.headers["retry-after"]) <= 60
    assert client.get("/health").status_code == 200  # health is never limited


def test_limiter_window_resets_and_is_per_ip():
    lim = FixedWindowLimiter(2, window_s=60)
    assert [lim.hit("a", 0), lim.hit("a", 1), lim.hit("a", 2) > 0] == [0, 0, True]
    assert lim.hit("b", 2) == 0  # another IP has its own budget
    assert lim.hit("a", 61) == 0  # new window


def test_body_over_limit_rejected_413():
    r = client.post("/v1/predict", content=b'{"text": "' + b"a" * (main.MAX_BODY_BYTES + 1) + b'"}',
                    headers={"content-type": "application/json"})
    assert r.status_code == 413


def test_chunked_body_over_limit_rejected_413():
    def gen():  # no Content-Length header -> chunked
        yield b'{"text": "'
        for _ in range(64):
            yield b"a" * 1024
        yield b'"}'
    r = client.post("/v1/predict", content=gen(), headers={"content-type": "application/json"})
    assert r.status_code == 413


def test_max_length_emoji_text_still_fits():
    r = client.post("/v1/predict", json={"text": "😀" * main.MAX_CHARS})  # \\ud83d\\ude00 escapes
    assert r.status_code == 200


def test_cors_allowed_origin():
    r = client.post("/v1/predict", json={"text": OK_TEXT}, headers={"origin": "http://localhost:8080"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:8080"


def test_cors_other_origin_not_allowed():
    r = client.options("/v1/predict", headers={"origin": "https://evil.example",
                                               "access-control-request-method": "POST"})
    assert r.status_code == 400
    assert "access-control-allow-origin" not in r.headers
    r = client.post("/v1/predict", json={"text": OK_TEXT}, headers={"origin": "https://evil.example"})
    assert "access-control-allow-origin" not in r.headers


# ---- Request ID (issue #8, plans/2026-11-16-request-id.md)
import logging
import re

RID = re.compile(r"^[A-Za-z0-9-]{8,64}$")


def test_request_id_header_present_and_unique():
    a = client.post("/v1/predict", json={"text": OK_TEXT}).headers.get("x-request-id")
    b = client.post("/v1/predict", json={"text": OK_TEXT}).headers.get("x-request-id")
    h = client.get("/health").headers.get("x-request-id")
    assert a and b and h and a != b
    assert all(RID.match(x) for x in (a, b, h))


def test_valid_incoming_request_id_is_reused():
    r = client.post("/v1/predict", json={"text": OK_TEXT}, headers={"X-Request-ID": "abc123-def456"})
    assert r.headers["x-request-id"] == "abc123-def456"


@pytest.mark.parametrize("bad", ["short", "a" * 65, "abc123 def456", "abc123def456\nINFO fake log", "abc_123_def_456", "../../etc"])
def test_invalid_incoming_request_id_is_replaced(bad):
    r = client.post("/v1/predict", json={"text": OK_TEXT}, headers={"X-Request-ID": bad.replace("\n", "%0A")})
    rid = r.headers["x-request-id"]
    assert rid != bad and RID.match(rid)


def test_request_id_in_predict_log_without_message_text(caplog):
    with caplog.at_level(logging.INFO, logger="phishguard"):
        r = client.post("/v1/predict", json={"text": "rahasia-unik-5521 " + OK_TEXT})
    rid = r.headers["x-request-id"]
    lines = [rec.getMessage() for rec in caplog.records if rec.getMessage().startswith("predict ")]
    assert len(lines) == 1 and f"id={rid} " in lines[0]
    assert "rahasia-unik-5521" not in caplog.text


def test_rejected_requests_also_carry_request_id(small_limit):
    big = client.post("/v1/predict", content=b'{"text":"' + b"a" * 40_000 + b'"}', headers={"content-type": "application/json"})
    assert big.status_code == 413 and RID.match(big.headers["x-request-id"])
    bad = client.post("/v1/predict", json={"text": "   "})
    assert bad.status_code == 422 and RID.match(bad.headers["x-request-id"])
    codes = [client.post("/v1/predict", json={"text": OK_TEXT}) for _ in range(5)]
    limited = [r for r in codes if r.status_code == 429]
    assert limited and all(RID.match(r.headers["x-request-id"]) for r in limited)


def test_cors_exposes_request_id_header():
    r = client.post("/v1/predict", json={"text": OK_TEXT}, headers={"Origin": "http://localhost:8080"})
    assert "x-request-id" in r.headers.get("access-control-expose-headers", "").lower()
