# Plan: Dataset judi online (judol) + perbaikan false negative

Tanggal: 2026-11-12 · Status: **selesai (14.40), live di URL publik**
Permintaan user: "nah mungkin perlu dataset untuk judol ya, tolong kerjakan semuanya, make no mistake".
Lanjutan dari `plans/2026-11-12-false-negative-obfuskasi.md` (bagian "Catatan review").

## Keputusan label
- Promosi judi online diberi label **phishing**. Ini berbeda dari kebijakan lama "spam/promo → aman" (`data/README.md`).
  Alasan: judol ilegal di Indonesia, situsnya tujuan penipuan/pencurian data, dan user meminta judol terdeteksi.
  Promo dagang resmi (diskon, kuota, kode voucher) tetap **aman**.
- Postingan bukan judol dari dataset yang sama (berita, kampanye anti-judol, konten biasa yang terkumpul dengan kata kunci judol) → **aman**.
  Ini hard negative yang mencegah model menandai setiap kata "judi" sebagai phishing.

## Sumber data (dicek 2026-11-12)
- Ekaputra, D. R. (2026). *Indonesian Online Gambling Promotion Multimodal Dataset* [Data set]. Hugging Face.
  https://huggingface.co/datasets/0xRafie/indonesian-gambling-multimodal-dataset. Lisensi **CC BY 4.0** (README dan tag HF), ITS.
  Isi: 5.028 posting Facebook/TikTok/X, kolom `text_caption`, `label` 1.0 = promosi judol, 0.0 = bukan; anotasi manual.
  Hanya `dataset.csv` yang diunduh (gambar tidak dipakai).
- Ditolak: `KagChi/indonesian-gambling-words` (hanya daftar kata, CC BY-NC-ND), `indirapravianti/online_gambling_yt_comments`,
  `treamyracle/*`, `jelialmutaali/*`, `yorris/*` (tidak mencantumkan lisensi).
- Catatan domain: teks berasal dari caption media sosial, bukan SMS. Bahasa promosinya sama (situs, bonus, gacor, link), tetapi panjang dan gaya berbeda.

## Langkah
1. Unduh `dataset.csv` ke `data/raw/indo/judol_0xrafie/` + catat sha256; periksa isi (contoh per label, panjang, duplikat, data pribadi seperti nomor HP/username).
2. Tambahkan ke `src/data/prepare_dataset.py` (sumber `judol_0xrafie`), dedup dengan data lama, split stratified per (label, sumber) seperti sebelumnya.
3. Latih ulang (`src/model/train.py`), bandingkan metrik dengan model lama **pada test set lama** (sumber non-judol) dan per sumber;
   simpan metrik lama sebelum retrain. Syarat: F1 phishing pada sumber lama tidak turun berarti, akurasi ≥ 85%, F1 ≥ 0,85.
4. Lapisan aturan: tambah TLD `mom` (dan TLD lain yang benar-benar muncul di data judol); rule `online_gambling` sempit (kosakata judol + domain/link),
   normalisasi angka→huruf hanya untuk pencocokan rule. Syarat: **0 false alarm** di seluruh pesan aman (lama + baru), tes pytest baru.
5. Uji: teks dari user (`Ke cici01 peener1ma THR ...`), versi bersihnya, promo judol, dan contoh aman serupa (promo THR resmi, berita judol).
   Challenge set v1/v2 tidak boleh turun. 36+ pytest lulus, tes Flutter lulus.
6. Rebuild container, uji ulang di URL live.
7. Perbarui `data/README.md`, README, Laporan (data, hasil, keterbatasan, pustaka), plan ini.

## Hasil
**Data** (`src/data/prepare_dataset.py`, sumber `judol_0xrafie`): 3.861 baris unik (1.499 judol → phishing, 2.362 bukan → aman) dari 5.028 (angka setelah perbaikan filter privasi 18.30, lihat bawah).
Dibuang: nomor telepon / `wa.me` / ID profil FB 36, Turki 251, non-Latin 48, > 2.000 karakter 27, < 3 kata ±640 (sebagian tumpang tindih); `@username` → `@user`.
Dua bug saya tangkap saat memeriksa jumlah baris: (1) `read_rows` memakai `splitlines()` sehingga caption multi-baris rusak → judol dibaca dengan
`csv` langsung (sumber lama tidak diubah); (2) regex Turki dengan `re.I` membuat `İ` cocok dengan `i` → huruf Turki dicocokkan tanpa `re.I`.
Split sumber lama terverifikasi identik (5.654/1.413). File mentah tidak di repo (nomor HP/username) → `data/raw/indo/judol_0xrafie/SOURCE.md` (URL revisi + sha256).

**Ruling: data judol tidak dicampur ke model utama.** Percobaan (scratchpad `exp/variants.py`, `exp/weights.py`):

| Varian | F1 test SMS lama | recall curated 2022+ | challenge v1 | v2 |
|---|---|---|---|---|
| tanpa judol (model lama) | 0,921 | 0,929 | 9/9 | 8/12 |
| semua judol dicampur | 0,903 | 0,643 | 5/9 | 7/12 |
| subsampel 300+300 | 0,915 | 0,857 | 8/9 | 8/12 |
| bobot per sumber 0,1–1,0 | 0,902–0,912 | 0,71–0,79 | 6/9 | 8/12 |

Semua varian menurunkan deteksi smishing Indonesia, dan **tidak satu pun** membuat pesan THR dari user terdeteksi (p 0,19–0,29).
Keputusan: model utama tetap dilatih dari sumber SMS saja; data judol melatih **detektor judol** terpisah (fitur + LR sama, target "promosi judol").
Kerugian kalau salah: dua model per request (latency p95 5,3 → 8,3 ms, bundle 1,8 → 5,6 MB).

**Model** (`src/model/train.py`, versi `tfidf_logreg-20261112`): model utama identik dengan sebelumnya (test 1.413: akurasi 0,978, F1 0,921, CM sama;
per bahasa/sumber dan challenge sama persis). CV berubah 0,919 → 0,923 hanya karena urutan baris train berubah.
Detektor judol (ambang 0,5, tidak dituning): test judol 772 → P 0,976, R 0,933, F1 0,954 (CM [[465,7],[20,280]]); **0 dari 6.089 SMS aman** menyalakan detektor.
Sistem (utama ATAU judol) pada posting judol: precision 0,648 karena model utama menandai 152 posting medsos biasa (perilaku lama, di luar domain SMS).

**Aturan** (`api/app/rules.py`): TLD baru `mom|lat|love|ink|lol|guru|bet|space|bio|group` (yang terlihat di data judol + kasus user);
rule `online_gambling` = domain berkosakata judi, atau ≥ 2 istilah promo judol + tautan/ajakan daftar, dicocokkan pada salinan ternormalisasi
(angka→huruf, huruf berulang dipadatkan). 0 hit pada 6.089 SMS aman dan 2.362 posting bukan judol; 427/1.499 judol.

**API** (`api/app/main.py`): bundle opsional `judol`; phishing bila model utama, detektor judol, atau aturan menandai; alasan
"Terindikasi promosi judi online (model deteksi judol)" kalau aturan judol tidak menyala.

**Bukti**
- TDD: 10 tes baru di `api/tests/test_rules.py` (6 gagal dulu, lalu lulus); total 46 pytest + 14 tes Flutter lulus.
- Seluruh 7.067 SMS lewat logika API sebelum vs sesudah: aman ditandai 34 → 34, phishing terdeteksi 962 → 962, **0 label berubah**.
- URL publik: pesan user → PHISHING 0,9 "Tautan 'akaligabandar.mom' memakai kosakata judi online"; versi ejaan bersih → phishing 0,9;
  promo judol tanpa tautan → phishing 0,9989 (detektor); kampanye anti-judol → aman 0,53; kode diskon THR Matahari → aman 0,89; apk → phishing 0,95.
  Chrome ke URL publik: kartu PHISHING 90% dengan alasan situs judol.
- Latency 55 request localhost:8000: p50 5,3 ms, p95 8,3 ms, maks 13,5 ms.
- Laporan (43 hlm): 2.2, 2.3, 2.4, 4.1, 4.2, 5.2 (T-13, T-14), 5.4, 5.5, 5.6, 6.4, 7.1–7.3, ringkasan (323 kata), pustaka Ekaputra (2026).

**Catatan jujur**
- Kampanye anti-judol hanya aman 0,53 (dekat ambang); model utama yang menentukan, bukan detektor.
- Data judol = caption media sosial; kinerja pada SMS/WA judol asli belum terukur (perlu data dari kelompok).
- APK tidak perlu dibangun ulang (deteksi di server).

## Uji ulang menyeluruh (2026-11-12, 18.00–18.40), permintaan user: "tolong uji semua"
| Lapisan | Hasil |
|---|---|
| pytest API | 46 lulus |
| Flutter | 14 tes lulus, `flutter analyze` bersih |
| Reproduksi data + model | `prepare_dataset.py` menghasilkan CSV dengan md5 identik; `train.py` hanya beda `trained_at` dan waktu prediksi |
| Model di container | md5 `/srv/model/phishguard.joblib` = `model/phishguard.joblib` |
| 11 kasus (judol user, ejaan bersih, promo judol, .apk, BCA palsu, spam EN, anti-judol, rapat, promo THR resmi, obrolan) | 11/11 sesuai di :8000, :8080, dan URL publik |
| Validasi | kosong 422, 2.002 karakter 422, 40 KB 413, JSON rusak 422, GET 405; `/docs` di :8080/publik hanya halaman SPA |
| Publik | http → 302 https, sertifikat berlaku s/d 10 Feb 2027, :8000 tidak terjangkau, Chrome: PHISHING 90% + alasan situs judol |
| Rate limit | 700 request paralel → 600×200, 100×429 dengan `retry-after` |
| Spoof X-Forwarded-For 7.7.7.7 | diabaikan di :8080 dan :8000 (tidak ada di log) |
| Aturan | 0 hit pada 8.451 pesan aman semua sumber |
| T-14 (7.067 SMS) | aman ditandai 34, phishing terdeteksi 962, detektor judol 0 kali menyala |
| Latency :8000 (55 request) | p50 5,4 ms, p95 6,5 ms, maks 7,9 ms |

**Bug yang ditemukan dan diperbaiki:** regex `PHONE` tidak mengenali `+62 878-...` (pemisah setelah 62), sehingga 4 baris judol
masih memuat nomor WA. Klaim sebelumnya "processed bebas nomor telepon" salah. Filter diperluas: nomor dengan pemisah, tautan
`wa.me/<nomor>` (nomor Malaysia/Kamboja ikut terbuang) dan `profile.php?id=` (ID profil Facebook pribadi). 10 baris judol dibuang;
split sumber SMS tetap identik (multiset train/test sama), model utama dan challenge tidak berubah, detektor dilatih ulang
(angka di atas sudah diperbarui), container API dibangun ulang, 46 pytest lulus. Pengecekan ulang: 0 baris judol cocok pola privasi.
Sisa yang disengaja: ID grup Facebook publik dan nominal uang.
