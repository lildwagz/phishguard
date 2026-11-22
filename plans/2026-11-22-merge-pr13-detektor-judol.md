# Plan: Merge PR #13 (issue #2) dan latih ulang detektor judol

Tanggal: 2026-11-22 · Status: **berjalan**
Permintaan user: "lanjut" (merge PR #13, latih ulang di `main`, rebuild API, perbarui README dan laporan).

## Latar
- Model 17 Nov: target detektor judol hanya `source == judol_0xrafie`, sehingga 31 SMS judol kelompok dilatih sebagai contoh bukan judol.
  Detektor hanya menangkap 1/31 (model 12 Nov: 13/31).
- PR #13 (opsi 1): kolom `modus` dibawa ke `data/processed/`; target detektor = judol_0xrafie atau `modus == "judi online"`, label phishing.
- Uji di worktree (hasil ditulis di issue #2): detektor pada SMS judol kelompok di test 1/7 → 4/7, 31 SMS 1/31 → 28/31,
  F1 posting judol 0,947 → 0,952, 0 false alarm pada 6.257 SMS aman; model utama dan split identik; 60 pytest.

## Langkah
1. Metrik lama ke `plans/metrics_before_pr13_2026-11-22.json`. Merge PR #13 (menutup issue #2).
2. Perapian kecil: baris kosong antar fungsi, `modus` di-`strip().lower()`. Cek test set tetap identik.
3. `prepare_dataset.py` + `train.py`, pytest, commit `data/processed/` + `model/`, push.
4. Rebuild container api; uji `/health` (versi model) dan kasus live, termasuk SMS judol.
5. README dan laporan (angka detektor judol); generate ulang PDF untuk diunggah manual ke Drive.
