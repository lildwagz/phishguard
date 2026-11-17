# Plan: Merge data kelompok (PR #12, issue #1) dan retrain

Tanggal: 2026-11-17 · Status: **berjalan**
Permintaan user: "oke jalankan" (perbaiki split, merge PR #12, retrain + tes + rebuild API, perbarui laporan dan README).

## Latar
- PR #12 (Data dan Model) menambah `data/raw/indo/kelompok/Intensifies.csv`: 337 baris, format `text,label,modus` sudah benar.
  Baris 1-102 SMS Indonesia 2025-2026 (50 phishing, 52 aman); sisanya SMS Nigeria berbahasa Inggris. User memutuskan sisanya dibiarkan (minor).
- Bug ditemukan saat uji di worktree: sumber `kelompok` memakai RNG bersama di `prepare_dataset.py`, sehingga menambah data kelompok
  mengacak ulang split sumber lama (849 pesan uji lama berpindah). Perbandingan sebelum/sesudah jadi tidak setara.

## Langkah
1. `OWN_RNG_SOURCES = {"judol_0xrafie", "kelompok"}` di `main`; cek test set lama identik setelah ditambah data kelompok. Commit, push.
2. Simpan metrik lama ke `plans/metrics_before_retrain_2026-11-17.json`. Merge PR #12 (menutup issue #1).
3. `prepare_dataset.py` + `train.py`, pytest, commit `data/processed/` + `model/`, push.
4. Rebuild container api; uji `/health` (versi model) dan 11 kasus live.
5. Laporan (angka evaluasi, data, ringkasan) dan README; generate ulang PDF, unggah ulang ke Drive.

## Hasil uji di worktree (test set lama yang sama, 1.413 pesan)
| Model | F1 test lama | F1 ID (test lama) | F1 test kelompok (61) | Challenge v1 / v2 |
|---|---|---|---|---|
| tanpa data kelompok | 0,921 | 0,944 | 0,19 | 9/9, 8/12 |
| + data kelompok | 0,916 | 0,938 | 0,83 | 8/9, 8/12 |
