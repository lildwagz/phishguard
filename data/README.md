# Data PhishGuard

`raw/` = file asli dari sumber (jangan diubah). `processed/` = hasil `python3 src/data/prepare_dataset.py` (bisa dibuat ulang kapan saja).

## Dataset yang dipakai

| Sumber | Bahasa | Label asli → label PhishGuard | Lisensi |
|---|---|---|---|
| `raw/mendeley_smishing/Dataset_5971.csv` — Mishra & Soni (2022) | EN | ham, spam → **aman** · smishing → **phishing** | CC BY 4.0 (Mendeley Data) |
| `raw/indo/rahmi2016/dataset_sms_spam_v1.csv` — Rahmi & Wibisono (2016) | ID | 0 normal, 2 promo → **aman** · 1 penipuan → **phishing** | CC BY-SA 4.0 |
| `raw/indo/bopbi/` — bopbi/indonesia-sms-spam-dataset (SMS asli, 2021) | ID | prize, loan, non-provider-promo → **phishing** · premium-sms → **aman** · evil-service dibuang | CC0 1.0 |
| `raw/indo/curated_2022plus/*.jsonl` — teks SMS/WA/posting penipuan **dikutip verbatim** dari berita & peringatan resmi 2022–2026 (kompas, liputan6, detik, tirto, turnbackhoax, bca.co.id, dll.) | ID | sudah berlabel; tiap baris punya `source_url` | kutipan untuk keperluan akademik, sumber dicantumkan per baris |
| `raw/indo/kelompok/*.csv` — SMS asli dari anggota kelompok (belum ada isinya) | ID | `text,label,modus` | data sendiri |

Catatan `curated_2022plus` (dikumpulkan 2026-11-12 oleh 4 agent riset paralel, lalu saya periksa):
69 penipuan (bank 25, lain-lain 35, kurir/APK/tilang 9) + 51 notifikasi resmi (40 ternyata sudah ada di Rahmi → terbuang saat dedup; 11 template OTP/pesanan WhatsApp Business dengan placeholder `{{1}}` diisi `482913`).
Sekitar 28 teks penipuan berasal dari **posting Facebook** (bukan SMS/WA) dan 7 teks BCA diketik ulang dari screenshot halaman edukasi BCA.
Teks dinormalisasi NFKC (huruf "math bold" → huruf biasa).

Spam/promo dimasukkan ke **aman**: PhishGuard menandai penipuan, bukan iklan.

**Hasil (`processed/`)**: 7.067 pesan unik (34 teks duplikat dengan label bertentangan dibuang), split stratified 80/20 per (label, sumber), seed 42.

_Tabel di bawah = versi pertama (sebelum data 2021+ ditambah); angka terbaru per sumber ada di output `prepare_dataset.py`._

| | aman EN | aman ID | phishing EN | phishing ID | total |
|---|---|---|---|---|---|
| train | 4.215 | 646 | 422 | 268 | 5.551 |
| test | 1.054 | 161 | 106 | 67 | 1.388 |

⚠️ Data tidak seimbang: phishing hanya ~12%. Model yang selalu menjawab "aman" sudah dapat akurasi ~88%,
karena itu NFR-03 direvisi menjadi akurasi ≥ 85% **dan F1 kelas phishing ≥ 0,85**; laporkan juga precision/recall.

Catatan: ~145 baris dari sumber Mendeley sudah berisi karakter rusak `�` sejak file aslinya (bukan dari proses kita).

## Disimpan tapi tidak dipakai (default)

- `raw/uci/` — UCI SMS Spam Collection (Almeida & Hidalgo, 2011; CC BY 4.0). Hanya ham/spam, dan ~4.753 barisnya sudah ada di dataset Mendeley.
- `raw/indo/ekaputra_sms-labeled-all.csv` — 20.829 SMS laporan pengguna laporsms.com (Penipuan / KTA / Lain-lain), dari github.com/ekaputra07/ina-sms-classifier.
  Tidak dipakai karena: (1) **tidak ada lisensi**, (2) labelnya berisik (promo pinjaman & judi online tercampur di "Penipuan"),
  (3) semuanya pesan yang dilaporkan, tidak ada SMS normal, (4) ada kolom `sender` berisi nomor HP asli.
  Karena tidak berlisensi, file ini **tidak ikut di repository publik** (`.gitignore`); hanya ada di laptop. Begitu juga `raw/indo/spacegoalex/` (tanpa lisensi, ditolak di `plans/2026-11-12-data-indonesia-terbaru.md`).

## Challenge set (`challenge/`) — tidak pernah dipakai training
- `challenge_id.csv` (9 pesan) — ditulis sebelum data 2022+ ditambahkan.
- `challenge_id_v2.csv` (12 pesan) — ditulis **setelah** retrain, jadi benar-benar belum pernah dilihat model. Ini ukuran paling jujur untuk modus baru.

## Sitasi (untuk Proposal/Laporan)

- Mishra, S., & Soni, D. (2022). *SMS Phishing Dataset for Machine Learning and Pattern Recognition* (Version 1) [Data set]. Mendeley Data. https://doi.org/10.17632/f45bkkt8pr.1
- Rahmi, F., & Wibisono, Y. (2016). *Aplikasi SMS Spam Filtering pada Android menggunakan Naive Bayes* [Unpublished manuscript]. Dataset v1.0 (2018): https://yudiwbs.wordpress.com/2018/08/05/dataset-klasifikasi-bahasa-indonesia-sms-spam-klasifikasi-teks-dengan-scikit-learn/
  - Sitasi & lisensi (CC BY-SA 4.0) diambil dari `penjelasan.txt` di arsip v1.0 (Agt 2018) pembuat dataset (https://bit.ly/yw_sms_spam_indonesia), disimpan tanpa diubah di `raw/indo/rahmi2016/penjelasan.txt`.
- bopbi. (2021). *Indonesia SMS Spam Dataset* [Data set]. GitHub. https://github.com/bopbi/indonesia-sms-spam-dataset (CC0 1.0)
- Almeida, T. A., & Hidalgo, J. M. G. (2011). *SMS Spam Collection* [Data set]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CC84

Checksum: `Dataset_5971.zip` sha256 `9bbf3188…233cc3` (cocok dengan Mendeley); `dataset_sms_spam_v1.csv` sha256 `206e8cb1…d717c` (cocok dengan yang dicatat repo mirror).
