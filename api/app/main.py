"""PhishGuard REST API: GET /health, POST /v1/predict.

Privacy (NFR-02): the message text is only held in memory for the duration of the request.
It is never written to disk or to the logs; the log line records length, label and latency only.
"""
import logging
import os
import time
from pathlib import Path

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from app import rules
from app.security import BodySizeLimit, FixedWindowLimiter, RateLimit

MAX_CHARS = 2000
# 2000 characters as JSON, worst case \uXXXX\uXXXX escapes per emoji, is < 24 KB.
MAX_BODY_BYTES = int(os.environ.get("MAX_BODY_BYTES", 32 * 1024))
RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN", 60))  # per client IP, per worker
# Origins of the web build allowed to call the API from a browser (Android app is not affected by CORS).
CORS_ORIGINS = [o.strip() for o in os.environ.get(
    "CORS_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(",") if o.strip()]
MODEL_PATH = Path(os.environ.get("MODEL_PATH", Path(__file__).resolve().parents[2] / "model" / "phishguard.joblib"))

log = logging.getLogger("phishguard")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

bundle = joblib.load(MODEL_PATH)
model = bundle["pipeline"]
MODEL_VERSION = f'{bundle["name"]}-{bundle["version"]}'
# Optional online-gambling (judol) detector trained by src/model/train.py; older bundles do not have it.
judol = bundle.get("judol")
JUDOL_REASON = "Terindikasi promosi judi online (model deteksi judol)"

app = FastAPI(title="PhishGuard API", version="1.0.0")
limiter = FixedWindowLimiter(RATE_LIMIT_PER_MIN)
# Order: the last added middleware runs first -> CORS, then rate limit, then body size, then the app.
app.add_middleware(BodySizeLimit, max_bytes=MAX_BODY_BYTES)
app.add_middleware(RateLimit, get_limiter=lambda: limiter, paths=("/v1/predict",))
# Only the web build's origin may call from a browser; no cookies/credentials are used.
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["GET", "POST"],
                   allow_headers=["content-type"])


class PredictRequest(BaseModel):
    text: str = Field(..., max_length=MAX_CHARS, description="Isi SMS/email yang akan dianalisis")

    @field_validator("text")
    @classmethod
    def not_blank(cls, v: str) -> str:  # FR-02
        if not v.strip():
            raise ValueError("Teks pesan tidak boleh kosong")
        return v


class PredictResponse(BaseModel):
    label: str  # "phishing" | "aman"
    confidence: float  # confidence in the returned label, 0..1
    model_version: str
    latency_ms: float
    reasons: list[str] = []  # human-readable rule hits (empty if only the ML model decided)


@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION}


@app.post("/v1/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    t0 = time.perf_counter()
    proba = dict(zip(model.classes_, model.predict_proba([req.text])[0]))
    hits = rules.check(req.text)
    reasons = [h.reason for h in hits]
    scores = [float(proba["phishing"])] + [h.score for h in hits]
    judol_hit = False
    if judol is not None:
        p_judol = float(judol["pipeline"].predict_proba([req.text])[0][1])
        if p_judol >= judol["threshold"]:
            judol_hit = True
            scores.append(p_judol)
            if not any(h.id == "online_gambling" for h in hits):  # one gambling reason is enough
                reasons.append(JUDOL_REASON)
    # Final decision: phishing if the main model, the judol detector OR any rule says so
    # (rules and the judol detector only ever add phishing signals).
    if proba["phishing"] >= 0.5 or hits or judol_hit:
        label = "phishing"
        confidence = max(scores)
    else:
        label, confidence = "aman", float(proba["aman"])
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    log.info("predict len=%d label=%s confidence=%.3f rules=%s judol=%s latency_ms=%.2f",
             len(req.text), label, confidence, ",".join(h.id for h in hits) or "-", judol_hit, latency_ms)
    return PredictResponse(label=label, confidence=round(confidence, 4), model_version=MODEL_VERSION,
                           latency_ms=latency_ms, reasons=reasons)
