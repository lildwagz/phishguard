import logging
import statistics
import time

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PHISH_ID = "Selamat! No anda terpilih mendapatkan cek tunai Rp175jt dari Shopee. Info klik: bit.ly/hadiah-shopee77 PIN 25f4777"
PHISH_EN = "URGENT: Your bank account has been suspended. Verify your details now at http://secure-bank-verify.co to avoid closure"
AMAN_ID = "Nanti sore jadi kumpul kelompok di perpustakaan jam 4 ya, bawa laptop buat ngerjain laporan"
AMAN_EN = "Hey, are we still meeting for lunch tomorrow at 12? Let me know"


def predict(text):
    return client.post("/v1/predict", json={"text": text})


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_predict_contract():
    body = predict(AMAN_EN).json()
    assert set(body) == {"label", "confidence", "model_version", "latency_ms", "reasons"}
    assert body["label"] in {"phishing", "aman"}
    assert 0.5 <= body["confidence"] <= 1.0


def test_phishing_examples():
    for text in (PHISH_ID, PHISH_EN):
        assert predict(text).json()["label"] == "phishing", text


def test_safe_examples():
    for text in (AMAN_ID, AMAN_EN):
        assert predict(text).json()["label"] == "aman", text


def test_empty_and_blank_rejected():  # FR-02
    for payload in ({"text": ""}, {"text": "   \n "}, {}):
        r = client.post("/v1/predict", json=payload)
        assert r.status_code == 422


def test_too_long_rejected():
    assert predict("a" * 2001).status_code == 422


def test_message_text_not_logged(caplog):  # NFR-02
    secret = "rahasia-unik-8841 klik bit.ly/xyz untuk hadiah"
    with caplog.at_level(logging.DEBUG):
        predict(secret)
    assert "rahasia-unik-8841" not in caplog.text
    assert "predict len=" in caplog.text


def test_latency_p95_under_3s():  # NFR-01 (in-process; Docker check is in README)
    times = []
    for i in range(100):
        t0 = time.perf_counter()
        assert predict(f"{PHISH_ID} {i}").status_code == 200
        times.append(time.perf_counter() - t0)
    p95 = statistics.quantiles(times, n=20)[18]
    assert p95 < 3.0
