# Plan: Melengkapi laporan (identitas, unduh APK, QA, Figma, peran)

Tanggal: 2026-11-22 · Status: **selesai; sisa placeholder menunggu data dari user**
Permintaan user: "kalo laporan ada yg kurang?" lalu memberi kelas 10.5A.01, semester 5, tahun akademik 2026/2027.

## Perubahan (docs/laporan_src, lokal; docs/ tidak masuk repo)
- Identitas: kelas dan semester/tahun akademik di sampul dan tabel identitas (fill.py mengganti [Kode Kelas] dan [Semester/Tahun Akademik]).
- 3.2, 4.3, 5.3, 6.3, 7.2: alamat server bawaan APK 1.0.0+2 = URL publik; tombol unduh APK di web; keterbatasan "isi alamat manual" dinyatakan sudah diperbaiki.
- 4.3: desain Figma (issue #3) dan status penerapannya (issue #10 belum dikerjakan).
- 4.5: daftar peran dan bukti kontribusi per anggota (dari identitas_kelompok.py lokal).
- 5.3, 7.1–7.3: hasil QA issue #5 (F1–F10 sesuai, variasi huruf berspasi lolos dan diuji ulang di API live, 10 pesan asli:
  3/3 penipuan tertangkap dan 2/7 promo resmi false alarm, uji pengguna 3 peserta skor 4,3/5). Waktu tugas peserta tertulis
  dalam ms (latency API), jadi tidak dikutip. Data perangkat di ringkasan QA tidak konsisten dengan komentar awal, jadi tidak dikutip.
- T-09 17/17 tes Flutter; checklist penyerahan semua dicentang (live app, stress test, kontribusi sudah ada buktinya).
- 52 halaman. Diunggah ke Drive sebagai Laporan_PhishGuard_2026-11-22.pdf/.docx (file lama tidak dihapus).

## Masih placeholder
Nomor/nama kelompok, tanggal, nama dosen, NIDN. Tag release v1.0.0 (#9) menunggu izin.
