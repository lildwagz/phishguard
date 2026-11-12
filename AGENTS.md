# AGENTS.md — PhishGuard

Instructions for any AI agent (Claude Code or otherwise) working in this directory.

## What this is

Student group project for the "Kecerdasan Buatan" (AI) course, kode MK 788, UBSI — a semester-long PBL (Project-Based Learning) assignment: build a full AI application (Flutter UI + REST API + model inference + deployment), graded via a Proposal and a final Laporan. Chosen case study: **PhishGuard**, an SMS/Email phishing text classifier (output: Phishing/Aman + confidence score).

**Always read `README.md` first** — it holds the current status checklist, architecture, defined requirements (FR/NFR), folder layout, and the next-steps list. This file (AGENTS.md) holds conventions and guardrails; README.md holds state. Update README.md's checklist whenever you complete a step — don't let it go stale.

## Conventions / guardrails

- Target stack: Flutter (mobile UI) → REST API (Flask or FastAPI) → AI service (TF-IDF + Naive Bayes/Logistic Regression for the first iteration) → optional data/log store → Docker deployment.
- `materi-kuliah/*.pdf` are the course's shared weekly slide decks (Pertemuan 1–16) — reference material only, read-only, never edit or delete.
- `docs/Template_Proposal_*.docx` and `docs/Template_Laporan_*.docx` are the official UBSI templates for the two graded deliverables — copy before filling in, never overwrite the blank template itself.
- Group number/class code/member names (NIM, nama mahasiswa) are intentionally left as placeholders in `docs/Checkpoint1_PhishGuard_RancanganAwal.docx` — that's the user's own data; never invent or guess it, ask the user.
- Flutter SDK 3.47.9 (official stable tarball) is installed at `~/development/flutter` — not on PATH by default: `export PATH="$HOME/development/flutter/bin:$PATH"`. Android toolchain installed 2026-11-12: JDK 21 (apt), SDK at `~/Android/Sdk`, AVD `phishguard_test`. **RAM is only 7 GB: never run a Gradle build while the emulator is up** (the kernel OOM-killed the emulator once) — build with `nice -n 19`, then `./gradlew --stop`, then start the emulator with `-memory 1536`. No Linux-desktop toolchain.
- Python work uses the project `.venv` (`requirements-dev.txt`). The API pins scikit-learn/joblib to the versions that trained `model/phishguard.joblib` — retrain the model if you bump them.
- This user prefers **apt or an official .deb/PPA** over snap for installing new software on this machine (a standing preference, not project-specific — don't propose snap installs here either).
- **Plans, research notes and decision write-ups always go in `plans/`** as dated files (e.g. `plans/2026-11-12-dataset.md`) — the user's explicit standing request. README.md holds status only.
- `data/raw/` holds unmodified downloads — never edit; regenerate `data/processed/` with `src/data/prepare_dataset.py`.
- When you advance the project (new code, dataset chosen, API built, etc.), update `README.md`'s status checklist and folder structure section to match reality.

## Where things are

```
PhishGuard/
├── README.md         — current status, architecture, requirements, next steps (read this first)
├── AGENTS.md         — this file: conventions and guardrails
├── docs/             — Checkpoint 1 (done) + official Proposal/Laporan templates (blank)
├── materi-kuliah/    — 16 course slide PDFs, read-only reference
├── mockups/          — source PNGs for the architecture diagram and Flutter UI mockup used in Checkpoint 1
├── plans/            — plans & research notes (one dated file per topic)
├── data/             — raw/ (untouched sources), processed/ (train/test), README.md (licences, citations)
├── src/              — data prep + model training scripts
├── model/            — trained model + metrics.json
├── api/              — FastAPI service + tests + Dockerfile
└── mobile/           — Flutter app
```
