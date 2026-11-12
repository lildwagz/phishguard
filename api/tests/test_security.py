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
