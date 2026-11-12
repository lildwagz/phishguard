import os

# The latency test sends 100+ requests from one client; the real limit is tested with its own limiter.
os.environ.setdefault("RATE_LIMIT_PER_MIN", "100000")
