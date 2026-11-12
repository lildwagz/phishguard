# Build from the project root:  docker compose build   (context needs model/ and api/)
FROM python:3.14-slim
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MODEL_PATH=/srv/model/phishguard.joblib
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/app ./app
COPY model/phishguard.joblib ./model/phishguard.joblib
RUN useradd --system --no-create-home phishguard
USER phishguard
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
# 2 workers (rate limit is per worker), max 64 open connections (503 above), idle keep-alive closed after 5 s.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--limit-concurrency", "64", "--timeout-keep-alive", "5"]
