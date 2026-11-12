"""Build the binary PhishGuard SMS dataset (phishing vs aman) from the raw public sources.

Run from the project root:  python3 src/data/prepare_dataset.py
Inputs  : data/raw/mendeley_smishing/, data/raw/indo/{rahmi2016,bopbi,curated_2022plus}/
Outputs : data/processed/phishguard_sms.csv, train.csv, test.csv  (columns: text,label,lang,source)
"""
import csv
import json
import random
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
SEED = 42
TEST_FRAC = 0.2


def read_rows(path):
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1252", errors="replace")
    return list(csv.DictReader(text.splitlines()))


def mendeley():
    # ham -> aman, smishing -> phishing, spam (promo/marketing) -> aman: we only flag fraud.
    mapping = {"ham": "aman", "spam": "aman", "smishing": "phishing"}
    for r in read_rows(RAW / "mendeley_smishing" / "Dataset_5971.csv"):
        yield r["TEXT"], mapping[r["LABEL"].strip().lower()], "en", "mendeley_smishing"


def rahmi():
    # 0 normal -> aman, 1 penipuan -> phishing, 2 promo -> aman
    mapping = {"0": "aman", "1": "phishing", "2": "aman"}
    for r in read_rows(RAW / "indo" / "rahmi2016" / "dataset_sms_spam_v1.csv"):
        yield r["Teks"], mapping[r["label"].strip()], "id", "rahmi2016"


def bopbi():
    # CC0 real Indonesian SMS (2021), one message per .txt, folder = category.
    # prize (fake lottery) and loan (fake "tanpa agunan" loans) and non-provider-promo (iPhone 750rb) are fraud lures
    # -> phishing; premium-sms is a real (annoying) telco subscription offer -> aman; evil-service (dukun) skipped.
    mapping = {"prize": "phishing", "loan": "phishing", "non-provider-promo": "phishing", "premium-sms": "aman"}
    for folder, label in mapping.items():
        for f in sorted((RAW / "indo" / "bopbi" / folder).glob("*.txt")):
            yield f.read_text(encoding="utf-8", errors="replace"), label, "id", "bopbi2021"


def curated():
    # Verbatim scam / official-notification texts quoted in Indonesian news & official warnings (2022+).
    # Collected by hand-checked web research; every row keeps its source_url. See data/README.md.
    for f in sorted((RAW / "indo" / "curated_2022plus").glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                # WhatsApp Business templates use {{1}}/{{ID}} placeholders -> fill with a realistic value
                text = re.sub(r"\{\{[^}]*\}\}", "482913", r["text"])
                yield text, r["label"], "id", "curated_2022plus"


def kelompok():
    # Real SMS/WA collected by group members (see data/raw/indo/kelompok/README.md). template.csv is skipped.
    for f in sorted((RAW / "indo" / "kelompok").glob("*.csv")):
        if f.name == "template.csv":
            continue
        for r in read_rows(f):
            yield r["text"], r["label"].strip().lower(), "id", "kelompok"


def norm(text):
    # NFKC turns decorative "math bold" Unicode letters used in scam posts into plain letters
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def main():
    seen, rows, conflicts = {}, [], 0
    for text, label, lang, source in [*mendeley(), *rahmi(), *bopbi(), *curated(), *kelompok()]:
        text = norm(text)
        if not text:
            continue
        key = text.lower()
        if key in seen:
            if seen[key]["label"] != label:  # same text, different label -> drop both, ambiguous
                seen[key]["label"] = None
                conflicts += 1
            continue
        seen[key] = row = {"text": text, "label": label, "lang": lang, "source": source}
        rows.append(row)
    rows = [r for r in rows if r["label"]]

    # stratified split on (label, source) so every source (incl. the small modern Indonesian sets)
    # is represented in both train and test
    rng = random.Random(SEED)
    train, test = [], []
    for stratum in sorted({(r["label"], r["source"]) for r in rows}):
        group = [r for r in rows if (r["label"], r["source"]) == stratum]
        rng.shuffle(group)
        n_test = round(len(group) * TEST_FRAC)
        test += group[:n_test]
        train += group[n_test:]
    rng.shuffle(train)
    rng.shuffle(test)

    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in [("phishguard_sms.csv", rows), ("train.csv", train), ("test.csv", test)]:
        with open(OUT / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["text", "label", "lang", "source"])
            w.writeheader()
            w.writerows(data)

    print(f"total {len(rows)}  (dropped {conflicts} conflicting duplicates)")
    for name, data in [("all", rows), ("train", train), ("test", test)]:
        print(name, len(data), dict(sorted(Counter((r["label"], r["source"]) for r in data).items())))


if __name__ == "__main__":
    main()
