# Plan: Merge PR #13 (issue #2) dan latih ulang detektor judol

Tanggal: 2026-11-22 · Status: **selesai; laporan di Drive perlu diganti manual**
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

## Hasil (main)
- PR #13 di-merge (`d97a96b`), issue #2 tertutup. Perapian + retrain: `e58f187`, model `tfidf_logreg-20261122`.
- `train.csv`/`test.csv` isi teks identik dengan sebelumnya (hanya tambah kolom `modus`). Model utama sama: akurasi 0,972, F1 0,907, matriks [[1234, 17], [24, 199]].
- Detektor judol: positif latih 1.199 → 1.223; posting judol uji P 0,976 R 0,930 F1 0,952 (sebelumnya 0,975 / 0,920 / 0,947), matriks [[465, 7], [21, 279]];
  SMS judol kelompok di test 1/7 → 4/7; 31 SMS (train+test) 1/31 → 28/31; 0 false alarm pada 6.257 SMS aman.
- 60 pytest, 17 tes Flutter lulus. Container api dibangun ulang: `/health` lokal dan publik = `tfidf_logreg-20261122`.
  Publik: challenge v1+v2 lewat API 20/21 (sama), 7/7 SMS judol kelompok di test → phishing, QA F1–F10 10/10.
  F7 (kampanye anti-judol) aman dengan keyakinan 0,53; skor ini dari model utama yang tidak berubah (detektor 0,00 di model lama dan baru).
- Laporan (lokal): versi model dan aplikasi 1.0.0+2, 17 tes Flutter, 2.3 target detektor, 5.5 metrik detektor, 5.6 temuan keempat, 7.1, 7.3.
