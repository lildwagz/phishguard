# Laporan Full Testing — 2026-11-12 (02:13–02:20 WIB)

Semua lapisan diuji setelah fitur lapisan aturan + "Scan dengan PhishGuard". **Hasil: semua lulus**, 1 false alarm model yang sudah diketahui.

| # | Lapisan | Pengujian | Hasil |
|---|---|---|---|
| 1 | Data | `prepare_dataset.py` dijalankan ulang → `train.csv`/`test.csv` identik (md5) | ✅ reproducible |
| 2 | Model | `model/metrics.json`: akurasi 0,978 · precision 0,923 · recall 0,918 · F1 phishing 0,921 (EN 0,901 · ID 0,944) | ✅ NFR-03 revisi (akurasi ≥85% & F1 ≥0,85) |
| 3 | API unit | `pytest`: 29 tes (kontrak, FR-02 kosong/spasi/>2000, NFR-02 teks tidak di-log, latency, 19 tes aturan positif/negatif) | ✅ 29/29 |
| 4 | Docker live | container `api` = kode & model di disk (diff + sha256 sama); `/health` OK; kosong/spasi/2001 char → 422, 2000 char → 200 | ✅ |
| 4b | Docker live | challenge v1+v2 lewat API (model+aturan): 20/21 | ✅ (salah: notifikasi debit BCA asli → phishing, sudah diketahui) |
| 4c | NFR-01 | 300 request HTTP: p50 3,9 ms · p95 4,5 ms · max 6,5 ms (target ≤3 s) | ✅ |
| 4d | NFR-02 | teks pesan tidak muncul di log container (log hanya len/label/confidence/rules/latency) | ✅ |
| 4e | CORS | preflight dari origin :8080 → `access-control-allow-origin: *` | ✅ |
| 5 | Flutter | `flutter analyze` 0 issue · `flutter test` 8/8 (5 app utama + 3 popup scan) | ✅ |
| 6 | Web e2e (Chrome headless) | kosong → pesan error; APK → PHISHING 95% + alasan; masuk riwayat | ✅ |
| 7 | Android (emulator API 36, APK release) | terdaftar sebagai handler `PROCESS_TEXT`; izin hanya `INTERNET` | ✅ |
| 7b | App utama | kosong → "Teks pesan tidak boleh kosong"; DANA domain palsu → PHISHING 85% + alasan; pesan rapat → AMAN 98,6%; riwayat tersimpan | ✅ |
| 7c | Scan popup (cold start, app di-force-stop dulu) | APK → PHISHING 95% (1,5 s buka); minta OTP → PHISHING 90%; OTP resmi WhatsApp → AMAN 83,6%; tombol Tutup kembali ke launcher | ✅ |
| 7d | Server mati | `docker compose stop api` → popup: "Tidak bisa terhubung ke server…" (tidak crash) | ✅ |
| 7e | Riwayat | hasil dari popup scan muncul di riwayat app utama | ✅ |

## Catatan
- Halaman web sempat terlihat kosong di Chrome headless: hanya karena render WebGL software butuh >6 detik; dengan jeda 14 detik normal. Bukan bug.
- **Sesi sebelumnya terhenti karena OOM**: kernel mematikan emulator (2 GB) saat Gradle build berjalan bersamaan di RAM 7 GB.
  Cara aman: build APK dulu (`nice -n 19`), hentikan daemon Gradle (`cd mobile/android && ./gradlew --stop`), baru nyalakan emulator (`-memory 1536`).
- Belum diuji otomatis: memilih teks sungguhan di aplikasi lain lewat sentuhan (yang diuji = intent `PROCESS_TEXT` yang sama yang dikirim menu seleksi teks). Uji manual di emulator/HP: tekan lama teks → ⋮ → "Scan dengan PhishGuard".
