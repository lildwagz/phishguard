# Plan: Perkuat model untuk modus penipuan Indonesia terbaru

Tanggal: 2026-11-12 · Status: **selesai (iterasi 1)** — model sudah dilatih ulang & di-deploy
Masalah: challenge set `data/challenge/challenge_id.csv` → hanya 1/5 penipuan modern terdeteksi
(lolos: kurir palsu, APK undangan, tarif bank, minta OTP). Data ID yang ada dari 2016 (modus hadiah/undian).

## Langkah
1. Cari dataset publik SMS/WA penipuan bahasa Indonesia yang lebih baru (2021+), cek lisensi & kualitas label.
2. Kalau tidak cukup: pertimbangkan sumber lain (ekaputra07/laporsms — tanpa lisensi; data sintetis — hati-hati bias).
3. Tambah ke `data/raw/`, perluas `prepare_dataset.py`, latih ulang.
4. Evaluasi jujur:
   - test set lama (jangan turun signifikan, terutama false positive pesan aman),
   - challenge set **diperluas** dengan contoh modus baru yang **tidak** berasal dari sumber training yang sama.
5. Rebuild Docker, update README/metrics.

## Aturan agar evaluasi tidak bocor
- Challenge set tidak boleh dipakai untuk training/tuning.
- Kalau ada data sintetis/tulisan sendiri di training, challenge set harus ditulis terpisah dan dicek tidak ada duplikat/near-duplicate.

## Hasil (2026-11-12)
**Pencarian dataset publik**: tidak ada dataset terbuka berisi modus 2022+ (kurir/APK/tarif bank/OTP).
- Dipakai: bopbi (CC0, 2021, 48 SMS asli).
- Ditolak: Zenodo 5554989 (= dataset Rahmi yang sama), spacegoalex (tanpa lisensi, spam & promo tercampur, repo baru 11 hari),
  SpamShield HF (gated, sebagian sintetis/terjemahan), ekaputra07 (tanpa lisensi, label berisik).

**Kurasi manual (4 sub-agent paralel)**: 69 teks penipuan + 11 notifikasi resmi baru, semua kutipan verbatim dengan `source_url`.
Kendala: kebanyakan berita hanya menampilkan screenshot → teks verbatim sedikit, terutama kurir/APK (9) dan notifikasi resmi.

**Hasil retrain** (sebelum → sesudah; snapshot lama: `plans/metrics_before_retrain_2026-11-12.json`):
| Metrik | Sebelum | Sesudah |
|---|---|---|
| CV F1 LogReg (train) | 0,907 | 0,919 |
| Test akurasi | 0,978 | 0,978 |
| Test F1 phishing | 0,914 | 0,921 |
| Test F1 phishing ID | 0,939 | 0,944 |
| Test sumber curated_2022plus (16) | — | 15/16 benar |
| challenge_id (9, ditulis sebelum retrain) | 5/9 (recall 1/5) | **9/9** |
| challenge_id_v2 (12, ditulis sesudah retrain, unseen) | — | **8/12** (recall 3/6, 1 false alarm) |

Masih lolos di v2: kurir APK, foto paket APK, lowongan part-time. False alarm: notifikasi transaksi debit BCA asli.
Catatan jujur: 9/9 di challenge v1 sebagian karena data kurasi berisi modus yang sama; v2 (8/12) lebih mencerminkan kondisi nyata.

## Kesimpulan & langkah berikutnya
- Bottleneck = **data**, bukan algoritma. Modus APK hampir tidak ada teks verbatim publiknya.
- Paling efektif: anggota kelompok mengumpulkan SMS/WA asli (penipuan **dan** notifikasi resmi bank/kurir/OTP) →
  `data/raw/indo/kelompok/` (README + template sudah disiapkan; otomatis ikut di `prepare_dataset.py`). Target ±100 pesan.
- Setelah data bertambah: latih ulang, cek `challenge_id_v2`, lalu tulis challenge v3 baru (jangan pernah dipakai training).
