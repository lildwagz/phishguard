"""Stress test PhishGuard (Laporan 5.4). See plans/2026-11-14-stress-test.md.

Run against the local stack (nginx -> API), with RATE_LIMIT_PER_MIN raised temporarily:
    locust -f tests/load/locustfile.py --host http://localhost:8080 --headless -u 50 -r 50 -t 60s --csv out/u50
Set NO_WAIT=1 for the capacity level (no think time between requests).
"""
import csv
import os
import random
from pathlib import Path

from locust import HttpUser, between, constant, task

TEST_CSV = Path(__file__).resolve().parents[2] / "data" / "processed" / "test.csv"
with open(TEST_CSV, encoding="utf-8") as f:
    TEXTS = [r["text"] for r in csv.DictReader(f) if 0 < len(r["text"]) <= 2000]


class PhishGuardUser(HttpUser):
    # A user reads the result before checking the next message; NO_WAIT=1 measures raw capacity.
    wait_time = constant(0) if os.environ.get("NO_WAIT") == "1" else between(0.5, 1.5)

    @task(19)
    def predict(self):
        self.client.post("/v1/predict", json={"text": random.choice(TEXTS)}, name="POST /v1/predict")

    @task(1)
    def health(self):
        self.client.get("/health", name="GET /health")
