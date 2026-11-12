"""Abuse protection for the public API (plans/2026-11-12-keamanan-api.md).

Pure ASGI middlewares, no extra dependencies:
- BodySizeLimit: rejects request bodies above MAX_BODY_BYTES with 413 *before* JSON parsing.
- RateLimit: fixed-window counter per client IP on /v1/predict, 429 + Retry-After when exceeded.

The limiter lives in process memory, so with N uvicorn workers the effective limit is up to N x the
configured value. Behind a reverse proxy (e.g. Tailscale Funnel) set uvicorn's FORWARDED_ALLOW_IPS to the
proxy address so the real client IP from X-Forwarded-For is used instead of the proxy's IP.
"""
import json
import math
import time


async def _send_json(send, status: int, detail: str, headers: list[tuple[bytes, bytes]] = ()):
    body = json.dumps({"detail": detail}).encode()
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json"),
                            (b"content-length", str(len(body)).encode()), *headers]})
    await send({"type": "http.response.body", "body": body})


class BodySizeLimit:
    def __init__(self, app, max_bytes: int):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        too_big = f"Body request maksimal {self.max_bytes} byte"
        for k, v in scope["headers"]:
            if k == b"content-length":
                try:
                    if int(v) > self.max_bytes:
                        return await _send_json(send, 413, too_big)
                except ValueError:
                    return await _send_json(send, 400, "Content-Length tidak valid")
        # Content-Length can be missing (chunked) or wrong: read the body ourselves, up to the limit.
        chunks, size = [], 0
        while True:
            msg = await receive()
            if msg["type"] == "http.disconnect":
                return
            chunk = msg.get("body", b"")
            size += len(chunk)
            if size > self.max_bytes:
                return await _send_json(send, 413, too_big)
            chunks.append(chunk)
            if not msg.get("more_body", False):
                break
        body, sent = b"".join(chunks), False

        async def replay():
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        return await self.app(scope, replay, send)


class FixedWindowLimiter:
    def __init__(self, limit: int, window_s: float = 60.0, max_keys: int = 10_000):
        self.limit, self.window_s, self.max_keys = limit, window_s, max_keys
        self._hits: dict[str, tuple[float, int]] = {}

    def hit(self, key: str, now: float | None = None) -> float:
        """Count one request; return 0 if allowed, else seconds until the window resets."""
        now = time.monotonic() if now is None else now
        start, count = self._hits.get(key, (now, 0))
        if now - start >= self.window_s:
            start, count = now, 0
        if count >= self.limit:
            return self.window_s - (now - start)
        if key not in self._hits and len(self._hits) >= self.max_keys:
            self._hits = {k: v for k, v in self._hits.items() if now - v[0] < self.window_s}
        self._hits[key] = (start, count + 1)
        return 0.0


class RateLimit:
    def __init__(self, app, get_limiter, paths: tuple[str, ...]):
        self.app, self.get_limiter, self.paths = app, get_limiter, paths

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["method"] == "POST" and scope["path"] in self.paths:
            ip = (scope.get("client") or ("unknown", 0))[0]
            wait = self.get_limiter().hit(ip)
            if wait:
                return await _send_json(send, 429, "Terlalu banyak permintaan, coba lagi sebentar",
                                        [(b"retry-after", str(math.ceil(wait)).encode())])
        return await self.app(scope, receive, send)
