"""Train the PhishGuard SMS classifier and write model/phishguard.joblib + model/metrics.json.

Run from the project root:  .venv/bin/python src/model/train.py
Compares TF-IDF + MultinomialNB against TF-IDF + LogisticRegression (5-fold CV F1 on train),
keeps the better one, then reports held-out test metrics overall and per language.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "model"
POS = "phishing"


def features():
    # word n-grams catch phrases ("klik link", "verify your account"); char n-grams catch
    # obfuscated spelling ("sh0pee", "m-dapatkan") and URL fragments in both languages.
    return FeatureUnion([
        ("word", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("char", TfidfVectorizer(lowercase=True, analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)),
    ])


CANDIDATES = {
    "tfidf_naive_bayes": lambda: Pipeline([("tfidf", features()), ("clf", MultinomialNB(alpha=0.1))]),
    "tfidf_logreg": lambda: Pipeline([
        ("tfidf", features()),
        ("clf", LogisticRegression(C=10, class_weight="balanced", max_iter=2000)),
    ]),
}


def scores(y_true, y_pred):
    return {
        "n": int(len(y_true)),
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision_phishing": round(precision_score(y_true, y_pred, pos_label=POS, zero_division=0), 4),
        "recall_phishing": round(recall_score(y_true, y_pred, pos_label=POS, zero_division=0), 4),
        "f1_phishing": round(f1_score(y_true, y_pred, pos_label=POS, zero_division=0), 4),
        "confusion_matrix [[aman->aman, aman->phish], [phish->aman, phish->phish]]":
            confusion_matrix(y_true, y_pred, labels=["aman", POS]).tolist(),
    }


def main():
    train = pd.read_csv(DATA / "train.csv")
    test = pd.read_csv(DATA / "test.csv")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_f1 = {}
    for name, make in CANDIDATES.items():
        s = cross_val_score(make(), train.text, train.label == POS, cv=cv, scoring="f1")
        cv_f1[name] = round(float(s.mean()), 4)
        print(f"CV F1 {name}: {s.mean():.4f} ± {s.std():.4f}")

    best = max(cv_f1, key=cv_f1.get)
    model = CANDIDATES[best]().fit(train.text, train.label)

    t0 = time.perf_counter()
    pred = model.predict(test.text)
    per_msg_ms = (time.perf_counter() - t0) / len(test) * 1000

    metrics = {
        "model": best,
        "version": datetime.now(timezone.utc).strftime("%Y%m%d"),
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cv_f1_phishing_train": cv_f1,
        "test_overall": scores(test.label, pred),
        "test_by_lang": {lang: scores(test.label[m], pred[m]) for lang in ["en", "id"] if (m := (test.lang == lang).values).any()},
        "test_by_source": {src: scores(test.label[m], pred[m]) for src in sorted(test.source.unique()) if (m := (test.source == src).values).any()},
        "baseline_always_aman_accuracy": round(float((test.label == "aman").mean()), 4),
        "avg_predict_ms_per_message": round(per_msg_ms, 3),
    }
    # NFR-03 (revised 2026-11-12): accuracy alone is misleading on imbalanced data, so F1 on phishing is required too.
    t = metrics["test_overall"]
    metrics["nfr03"] = {
        "target": "accuracy >= 0.85 and f1_phishing >= 0.85 on test set",
        "accuracy_ok": t["accuracy"] >= 0.85,
        "f1_phishing_ok": t["f1_phishing"] >= 0.85,
        "pass": t["accuracy"] >= 0.85 and t["f1_phishing"] >= 0.85,
    }

    # Hand-written modern Indonesian messages — NOT used for training, only to show real-world gaps.
    # v1 was written before the 2022+ curated data was added; v2 was written after that retrain (fully unseen).
    for path in sorted((ROOT / "data" / "challenge").glob("challenge_*.csv")):
        ch = pd.read_csv(path)
        ch_pred = model.predict(ch.text)
        metrics[path.stem] = {
            **scores(ch.label, ch_pred),
            "missed_phishing": ch.note[(ch.label == POS) & (ch_pred != POS)].tolist(),
            "false_alarm_aman": ch.note[(ch.label != POS) & (ch_pred == POS)].tolist(),
        }

    OUT.mkdir(exist_ok=True)
    joblib.dump({"pipeline": model, "version": metrics["version"], "name": best}, OUT / "phishguard.joblib")
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
