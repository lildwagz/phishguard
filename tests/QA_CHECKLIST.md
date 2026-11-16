# Checklist QA PhishGuard

Untuk QA / Tester. Centang setiap butir setelah diuji. Kalau hasilnya tidak sesuai, buat issue baru dengan label `bug` (format di bagian H)
dan tulis nomornya di samping butir, misalnya `gagal, lihat #12`.

Target: APK Android dan web di **https://phishguard.taile0ea7c.ts.net**.
Kalau URL tidak bisa dibuka, kabari ketua: server berjalan di laptop ketua dan harus menyala.

## A. Persiapan
- [ ] Catat perangkat: merek/tipe HP, versi Android, browser dan versinya, laptop (OS) untuk uji web.
- [ ] Pasang APK terbaru (minta ke ketua atau unduh dari GitHub Release bila sudah ada).
- [ ] Di aplikasi, buka ikon pengaturan (kanan atas) lalu isi alamat server `https://phishguard.taile0ea7c.ts.net`, tekan Simpan.
- [ ] Catat versi model yang tampil di kartu hasil (contoh `tfidf_logreg-20261112`).

## B. Fungsi utama (FR-01 sampai FR-04)
Pakai pesan contoh di bagian F.
- [ ] FR-01 pesan phishing: tempel, tekan Analisis → kartu **PHISHING** merah, ada persentase keyakinan.
- [ ] FR-01 pesan aman: → kartu **AMAN**, ada persentase keyakinan.
- [ ] FR-01 waktu: hasil muncul kurang dari 3 detik. Catat angka ms di bawah kartu hasil.
- [ ] Tombol Analisis tidak bisa ditekan berulang saat sedang memproses (ada indikator loading).
- [ ] FR-02 kosong: tekan Analisis tanpa teks → pesan "Teks pesan tidak boleh kosong".
- [ ] FR-02 hanya spasi → pesan yang sama.
- [ ] FR-02 panjang: tempel teks lebih dari 2.000 karakter → input berhenti di 2.000, penghitung terlihat (misal 2000/2000).
- [ ] FR-03 riwayat: hasil analisis muncul di "Riwayat (di perangkat ini)" dengan cuplikan, label, persentase, dan waktu.
- [ ] FR-03 riwayat tetap ada setelah aplikasi ditutup lalu dibuka lagi.
- [ ] FR-03 tombol Hapus mengosongkan riwayat.
- [ ] FR-03 (opsional) setelah lebih dari 50 analisis, riwayat hanya menyimpan 50 terakhir.
- [ ] FR-04 alasan muncul di bagian "Tanda bahaya terdeteksi" untuk: file .apk, minta kode OTP, kerja dibayar per tugas/like,
      domain tiruan bank/brand, promosi judi online (contoh F2, F3, F4, F5, F6).
- [ ] Hasil aman tidak menampilkan "Tanda bahaya", tetapi saran umum tetap ada.

## C. Scan dari aplikasi lain (FR-05, FR-06), khusus Android
- [ ] FR-05 seleksi teks: di Chrome atau aplikasi catatan, blok teks pesan → menu "Scan dengan PhishGuard" → popup hasil muncul.
- [ ] FR-05 cold start: tutup paksa PhishGuard dulu (hapus dari recent apps), ulangi → popup tetap muncul.
- [ ] FR-05 teks lebih dari 2.000 karakter → popup memberi keterangan teks dipotong.
- [ ] FR-06 SMS: di aplikasi Pesan, tekan lama sebuah SMS → Bagikan → "Scan dengan PhishGuard" → popup hasil.
- [ ] FR-06 WhatsApp: tekan lama pesan → Bagikan/Teruskan ke aplikasi lain → PhishGuard → popup hasil.

## D. Kondisi gagal
- [ ] Mode pesawat / data mati → pesan "Tidak bisa terhubung ke server ...", aplikasi tidak crash.
- [ ] Alamat server salah (isi `https://contoh-salah.invalid`) → pesan tidak bisa terhubung, tidak crash. Kembalikan alamat setelahnya.
- [ ] Koneksi lambat (sinyal lemah) → setelah ±10 detik muncul pesan gagal, bukan loading selamanya.
- [ ] Setelah kondisi gagal, koneksi dinyalakan lagi → analisis berikutnya berhasil.

## E. Web, tampilan, dan aksesibilitas
- [ ] Buka URL di Chrome HP → ulangi B (FR-01, FR-02, FR-03).
- [ ] Buka URL di Chrome laptop → tampilan tidak melebar penuh layar, tetap rapi.
- [ ] Teks bawah halaman menampilkan "Server: https://phishguard.taile0ea7c.ts.net".
- [ ] Label hasil terbaca tanpa melihat warna (ada teks PHISHING/AMAN dan ikon).
- [ ] Ukuran font HP diperbesar ke maksimum → teks tidak terpotong atau saling menimpa.
- [ ] Putar layar ke landscape → tampilan tetap bisa dipakai.

## F. Pesan contoh (hasil yang diharapkan)
| No | Pesan | Harapan |
|---|---|---|
| F1 | `Rapat kelompok besok jam 3 sore di perpustakaan ya, jangan lupa bawa laptop` | Aman |
| F2 | `J&T Express: paket Anda tertahan. Cek resi di aplikasi berikut J&T_Cek_Resi.apk` | Phishing + alasan .apk |
| F3 | `Selamat! Nomor Anda memenangkan hadiah Rp 100jt dari BCA. Klaim di bca-hadiah.xyz sekarang` | Phishing + alasan domain |
| F4 | `Mohon maaf saya salah kirim kode verifikasi ke nomor anda, tolong kirimkan kode 6 digit itu ke saya` | Phishing + alasan kode OTP |
| F5 | `Dibutuhkan pekerja paruh waktu, cukup like video TikTok dibayar 50rb per tugas, chat admin` | Phishing + alasan kerja per tugas |
| F6 | `Ke cici01 peener1ma THR 275.000! akaligabandar.mom aambil skrg pkai k0dee : PUASA2026` | Phishing + alasan judi online |
| F7 | `Stop judi online! Judol merusak keluarga, laporkan situs judi ke aduankonten.id` | Aman |
| F8 | `Belanja THR di Matahari diskon 50%, pakai kode THR2026 di matahari.co.id berlaku s/d 30 April` | Aman |
| F9 | `WINNER!! You have been selected to receive a 900 prize reward. Call 09061701461 to claim now` | Phishing |
| F10 | `Ok bro nanti aku kabari lagi habis maghrib` | Aman |

- [ ] Semua F1 sampai F10 diuji di APK. Tulis yang hasilnya berbeda dari harapan.
- [ ] Coba variasi penulisan dari F2 sampai F6 (kata diganti, ejaan diubah, spasi disisipkan) dan catat mana yang lolos sebagai aman
      atau kehilangan alasan. Contoh yang sudah diketahui lolos tanpa alasan: "Kode verifikasi sudah terkirim ke nomor kamu, tolong kirimkan kodenya ke saya ya" (tetap phishing, tetapi alasan OTP tidak muncul).
- [ ] Uji minimal 10 pesan asli dari HP sendiri atau anggota (penipuan dan notifikasi resmi). **Samarkan nama, nomor HP, dan nomor rekening
      sebelum ditulis di mana pun.** Catat: teks (sudah disamarkan), harapan, hasil, persentase. Kirim ke peran Data dan Model sebagai bahan data.

## G. Uji pengguna di luar kelompok (minimal 3 orang)
Tujuan: orang yang belum pernah melihat aplikasi bisa memakainya tanpa dibantu.
- [ ] Minta izin, jelaskan bahwa yang diuji aplikasinya, bukan orangnya. Jangan catat nama lengkap (cukup P1, P2, P3) dan umur kisaran.
- [ ] Tugas 1: "Periksa pesan ini apakah penipuan" (beri F3). Catat berhasil/tidak dan berapa detik.
- [ ] Tugas 2: "Periksa pesan ini" (beri F1). Catat apakah peserta paham arti hasil dan persentasenya.
- [ ] Tugas 3 (Android): "Periksa SMS ini langsung dari aplikasi Pesan" (FR-06). Catat apakah peserta menemukan menu Bagikan sendiri.
- [ ] Tanyakan: skor kemudahan 1 sampai 5, bagian yang membingungkan, apakah akan memakai aplikasi ini, saran.
- [ ] Tulis rangkuman di komentar issue: tabel peserta × tugas (berhasil/tidak, waktu), skor rata-rata, temuan utama.

## H. Format laporan bug (issue baru, label `bug`)
```
Judul: [singkat, misal "Popup scan tidak muncul dari WhatsApp"]
Perangkat: [HP, versi Android / browser]
Langkah: 1. ... 2. ... 3. ...
Harapan: ...
Kenyataan: ...
Bukti: [screenshot/rekaman layar; samarkan data pribadi]
Seberapa sering: [selalu / kadang / sekali]
```

## I. Selesai
- [ ] Semua butir A sampai G dicentang atau diberi nomor issue bug.
- [ ] Ringkasan di komentar issue: jumlah butir lulus/gagal, daftar bug yang dibuat, perangkat yang dipakai.
