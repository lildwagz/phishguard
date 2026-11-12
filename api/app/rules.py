"""High-precision phishing rules that complement the ML model.

The TF-IDF + Logistic Regression model only knows word patterns that appear in its training data.
These rules catch well-known Indonesian scam patterns that are (almost) absent from that data.
Each rule returns a human-readable reason (shown in the app) and a score used as confidence.
Keep rules narrow: a false alarm on a genuine bank/OTP message is worse than a miss the model may still catch.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RuleHit:
    id: str
    reason: str
    score: float


# --- 1. APK attachment -------------------------------------------------------------------------
APK = re.compile(r"\.apk\b", re.I)

# --- 2. Asking the reader to send / tell a code ------------------------------------------------
SHARE_VERB = re.compile(
    r"\b(kirim(?:kan)?|kirimin|sebutkan|sebutin|berikan|kasih(?:kan)?|bagikan|teruskan|forward|infokan|send|share|tell)\b"
    r"[^.!?\n]{0,40}?\b(kode|otp|pin(?!\s*(?:lokasi|location|point|map|maps)\b)|code)\b",
    re.I,
)
NEGATION = re.compile(r"\b(jangan|jgn|tidak|tdk|never|do not|don't|dont)\b[\s\w,]{0,15}$", re.I)

# --- 3. Paid "like / follow" tasks posing as a job ---------------------------------------------
TASK = re.compile(r"\b(like|likes|follow|subscribe|komen|komentar|tugas|rating|ulasan)\b", re.I)
# a pay *rate* ("50rb per tugas", "Rp100.000/hari") or explicit commission wording — a plain salary mention is not enough
MONEY = re.compile(
    r"((\brp\.?\s?[\d.,]+|\b\d+[\d.,]*\s?(rb|ribu|k|jt|juta))\s*(/|per\s)\s*(tugas|task|like|video|hari|jam|order)"
    r"|\bkomisi\b|\bdibayar\b|\bbayaran\b|\bupah\b)",
    re.I,
)
JOB = re.compile(r"\b(kerja|pekerjaan|paruh waktu|part[\s-]?time|freelance|penghasilan|lowongan|rekrut\w*|hrd?)\b", re.I)

# --- 4. Look-alike domains that borrow a brand name -------------------------------------------
# Only real-looking TLDs, so "dari BRI.Klaim sekarang" (missing space after a full stop) is not a domain.
TLDS = ("com|id|net|org|xyz|online|site|info|co|tk|cc|top|buzz|link|click|me|io|app|shop|store|vip|live|life|web"
        "|ly|gl|ml|ga|cf|gq|icu|cyou|sbs|pw|club|biz|asia|my|cloud|today|win|work")
DOMAIN = re.compile(rf"\b(?:https?://)?((?:[a-z0-9-]+\.)+(?:{TLDS})(?:\.[a-z]{{2}})?)(?![a-z0-9-])", re.I)
BRANDS = {
    "bca", "bri", "brimo", "bni", "mandiri", "livin", "btn", "bsi", "cimb", "danamon", "jenius", "ocbc",
    "dana", "ovo", "gopay", "shopee", "shopeepay", "tokopedia", "lazada", "gojek", "grab",
    "jnt", "jne", "sicepat", "anteraja", "posindonesia", "pos", "bpjs", "pln", "telkomsel", "indosat",
    "pajak", "coretax", "djp", "etilang", "tilang", "bansos", "kemensos", "ojk", "whatsapp",
}
OFFICIAL_SUFFIXES = (
    "bca.co.id", "klikbca.com", "bri.co.id", "bni.co.id", "bankmandiri.co.id", "btn.co.id", "bankbsi.co.id",
    "cimbniaga.co.id", "danamon.co.id", "jenius.com", "ocbc.id", "dana.id", "ovo.id", "gojek.com", "grab.com",
    "shopee.co.id", "tokopedia.com", "lazada.co.id", "jet.co.id", "jne.co.id", "sicepat.com", "anteraja.id",
    "posindonesia.co.id", "bpjs-kesehatan.go.id", "bpjsketenagakerjaan.go.id", "pln.co.id", "telkomsel.com",
    "tsel.me", "indosatooredoo.com", "indosat.com", "im3.id", "xl.co.id", "tri.co.id", "grab.co", "ojk.go.id", "pajak.go.id", "kemensos.go.id", "whatsapp.com", "wa.me",
    ".go.id",  # any Indonesian government domain
)


def _share_code_request(text: str) -> bool:
    for m in SHARE_VERB.finditer(text):
        if not NEGATION.search(text[: m.start()]):
            return True
    return False


def _lookalike_domain(text: str) -> str | None:
    for m in DOMAIN.finditer(text):
        domain = m.group(1).lower()
        if domain.endswith(OFFICIAL_SUFFIXES):
            continue
        tokens = set(re.split(r"[.-]", domain))
        if tokens & BRANDS:
            return domain
    return None


def check(text: str) -> list[RuleHit]:
    hits = []
    if APK.search(text):
        hits.append(RuleHit("apk_attachment", "Meminta membuka/menginstal file .apk (modus APK undangan/paket/tilang)", 0.95))
    if _share_code_request(text):
        hits.append(RuleHit("share_code_request", "Meminta Anda mengirim/menyebutkan kode OTP/verifikasi/PIN", 0.9))
    if TASK.search(text) and MONEY.search(text) and JOB.search(text):
        hits.append(RuleHit("paid_task_job", "Tawaran kerja dibayar untuk like/follow/tugas online", 0.85))
    if domain := _lookalike_domain(text):
        hits.append(RuleHit("lookalike_domain", f"Tautan '{domain}' memakai nama brand tapi bukan domain resmi", 0.85))
    return hits
