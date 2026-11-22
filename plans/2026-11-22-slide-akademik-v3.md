# Plan: Desain ulang slide UAS dengan skill academic-pptx (v3)

Tanggal: 2026-11-22 · Status: **selesai (2026-11-22)**
Permintaan user: "design ulang ppt kita menggunakan skill academic pptx agar lebih menarik". Outline 16 slide disetujui;
kelas/dosen dibiarkan kosong (tidak ditulis), warna default skill (navy 1F4E79, biru 2E75B6), user memasang libreoffice-impress untuk QA.

## Keputusan
- File baru `Slide_PhishGuard_v3.pptx` + PDF; slide Hafidz (issue #11) tidak diubah.
- Dibuat dengan pptxgenjs (skrip di `docs/slide_src/build_slides.js`, docs/ tidak masuk repo). Font Arial, latar putih,
  judul berupa kalimat kesimpulan, grafik native (bukan gambar) untuk metrik, maksimal ±40 kata per slide.
- Semua angka diambil dari `model/metrics.json` (tfidf_logreg-20261122), laporan, dan `plans/2026-11-14-stress-test.md`.
- Screenshot: `mockups/screenshots/android_2_phishing.png` dan `android_4_scan_popup.png` (tanpa nomor HP).
- Slide 11 berisi lima kegagalan (outline menyebut empat; temuan kelima = target detektor judol, PR #13).

## QA
validate.py, teks per slide, render PDF → gambar, cek overflow/tumpang tindih, checklist akademik.

## Hasil
- `docs/Slide_PhishGuard_v3.pptx` + `.pdf` (16 slide), dibangun dengan `node docs/slide_src/build_slides.js`
  (pptxgenjs 3.12.0 di luar repo, NODE_PATH). validate.py lulus.
- QA visual: render LibreOffice Impress (dipasang 2026-11-22). Perbaikan putaran 2: angka Rp9 triliun bertumpuk, judul kotak
  FastAPI, label grafik memakai format Inggris (PDF dirender dengan locale id-ID: 5.797; 0,921; 2.000 ms), teks terpotong, ukuran referensi.
- Catatan: label grafik di PPTX mengikuti locale PowerPoint penyaji (bisa tampil 0.921 di komputer berbahasa Inggris); PDF sudah format Indonesia.
- Diunggah ke Drive: Slide_PhishGuard_v3.pptx dan .pdf. Slide Hafidz tidak diubah.
