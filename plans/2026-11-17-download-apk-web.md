# Plan: Build ulang dan tombol unduh APK di web

Tanggal: 2026-11-17 · Status: **selesai**
Permintaan user: "build ulang dong, dan saya mau tambahkan download apk di webnya".

## Desain
- APK yang dibagikan lewat web harus langsung jalan di HP orang lain. Saat ini alamat bawaan Android `http://10.0.2.2:8000` (khusus emulator),
  sehingga pengguna harus mengisi alamat server manual (Laporan 7.2). Alamat bawaan Android dibuat bisa diatur saat build:
  `--dart-define=API_BASE_URL=https://phishguard.taile0ea7c.ts.net`; tanpa define tetap `10.0.2.2:8000` (emulator, pengembangan).
  Alamat yang disimpan pengguna lewat ikon pengaturan tetap didahulukan.
- Web: tombol "Unduh aplikasi Android (APK)" hanya tampil di versi web (`kIsWeb`; di aplikasi Android tidak perlu). Membuka `download/PhishGuard.apk`
  relatif terhadap halaman, lewat `url_launcher`.
- nginx (`mobile/nginx.conf`): `location /download/` dengan tipe `application/vnd.android.package-archive` dan `Content-Disposition: attachment`.
  `mobile/Dockerfile.web` menyalin `build/app/outputs/flutter-apk/app-release.apk` ke `/usr/share/nginx/html/download/PhishGuard.apk`.
- Versi aplikasi `1.0.0+1` jadi `1.0.0+2` agar bisa memperbarui APK lama yang sudah terpasang.
- Batasan yang dicatat: APK masih ditandatangani debug key (belum ada keystore rilis), dan Android akan meminta izin "instal dari sumber tidak dikenal".
- RAM: build Gradle hanya saat emulator mati, dengan `nice -n 19`.

## Langkah (TDD)
1. Tes gagal dulu: `baseUrlFor` Android memakai nilai define; widget test tombol unduh tampil bila diaktifkan dan tidak tampil bila tidak.
2. Implementasi; `flutter test` lulus.
3. `flutter build web --release`, `flutter build apk --release --dart-define=...`.
4. Rebuild container web; uji `/download/PhishGuard.apk` lokal dan publik (status, tipe, ukuran, checksum sama dengan file build), screenshot tombol di web.
5. README, plan, commit, push.

## Hasil
- TDD: 3 tes Flutter baru gagal dulu (parameter belum ada), lalu lulus. Total **17 tes Flutter** lulus, `flutter analyze` bersih.
- `url_launcher` ditambahkan. Versi 1.0.0+2 (versionCode 2, minSdk 24 = Android 7.0); alamat server publik tertanam di `libapp.so`.
- APK 51,3 MB, sha256 `61c587928e4d53a8c371d8b4b6edca33b9da9fee0390fc7d512e22615462c8f8`. `.dockerignore` mengizinkan file APK ini masuk konteks build.
- Uji: `/download/PhishGuard.apk` lokal dan publik → 200, `application/vnd.android.package-archive`, `Content-Disposition: attachment`, ukuran dan sha256 sama;
  file lain di `/download/` → 404; halaman utama 200; 11/11 kasus API live tetap lulus. Playwright (Chrome): tombol tampil di bawah riwayat, klik → unduhan `PhishGuard.apk` dengan sha256 sama.
- Belum: uji pasang APK baru di HP asli (unduh dari web, instal, analisis tanpa mengubah alamat server).
