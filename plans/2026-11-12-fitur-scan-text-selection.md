# Plan: Fitur "Scan via Text Selection" (ACTION_PROCESS_TEXT)

Tanggal: 2026-11-12 · Status: **direncanakan, belum dikerjakan** (stretch feature, bukan prioritas MVP)

## Ide

User select teks mencurigakan di app APAPUN (SMS, WhatsApp, Email, browser) → tekan lama → menu seleksi teks Android menampilkan "Scan dengan PhishGuard" sebagai salah satu opsi → tap → popup kecil muncul berisi hasil (Phishing/Aman + confidence), tanpa perlu buka aplikasi PhishGuard secara manual.

## Kenapa ini, bukan auto-scan SMS background

Dibahas sebelumnya: auto-scan SMS masuk (BroadcastReceiver + `RECEIVE_SMS`/`READ_SMS`) juga possible, tapi:
- Google Play membatasi izin SMS itu hanya untuk app default SMS handler.
- Android-only, dan hanya menyasar SMS (bukan WhatsApp/Email).
- Butuh background/foreground service yang jalan terus (baterai, kompleksitas).

Pendekatan **`ACTION_PROCESS_TEXT`** (standar Android text-selection toolbar — dipakai Google Translate, Grammarly, dll) lebih baik untuk kasus kita:
- Tidak butuh izin sensitif apa pun.
- Jalan di app apa pun yang mendukung seleksi teks, bukan cuma SMS.
- Tidak ada service background — hanya aktif saat user memilih fitur ini sendiri (user-initiated, bukan pasif/pantau terus).
- Implementasi jauh lebih sederhana: 1 Activity + 1 intent-filter.

## Desain teknis

1. **AndroidManifest.xml** (`mobile/android/app/src/main/AndroidManifest.xml`): tambah Activity baru (mis. `ScanTextActivity`) dengan intent-filter:
   ```xml
   <activity android:name=".ScanTextActivity"
             android:label="Scan dengan PhishGuard"
             android:theme="@style/Theme.Translucent.Dialog"
             android:excludeFromRecents="true">
     <intent-filter>
       <action android:name="android.intent.action.PROCESS_TEXT" />
       <category android:name="android.intent.category.DEFAULT" />
       <data android:mimeType="text/plain" />
     </intent-filter>
   </activity>
   ```
2. Activity menerima teks lewat extra `Intent.EXTRA_PROCESS_TEXT`, lempar ke Flutter lewat method channel (atau — lebih simpel — tulis activity ini di Flutter via `flutter_process_text`-style plugin / native code tipis yang langsung panggil Dart entrypoint terpisah).
3. UI popup: pakai tema dialog/translucent (bukan full screen) — tampilkan loading singkat → panggil `POST /v1/predict` (API yang sudah ada, tidak perlu endpoint baru) → tampilkan kartu hasil (label + confidence), tombol tutup.
4. Kalau teks > batas panjang (2000 karakter, sesuai FR-02 yang sudah ada di API) → potong atau beri pesan, konsisten dengan validasi yang sudah ada.
5. iOS (opsional, belakangan): padanannya adalah **Action Extension** yang muncul di menu share/selection teks — implementasi terpisah dari Android, native Swift, effort tambahan sendiri. Tidak prioritas untuk tugas kuliah ini.

## Dependensi

- Butuh pipeline build Android APK sudah jalan (Android Studio/SDK) — ini sendiri belum selesai di `plans/2026-11-12-build-mvp.md` / README langkah 2. Kerjakan fitur ini **setelah** APK dasar bisa di-build & di-install di HP.
- Tidak mengubah API/model yang sudah ada — murni tambahan di sisi `mobile/`.

## Kriteria selesai (verify)

- Select teks di app lain (mis. aplikasi SMS/Messages bawaan HP) → "PhishGuard" muncul di menu seleksi teks.
- Tap → popup muncul dengan hasil klasifikasi dalam ≤3 detik (NFR-01 tetap berlaku).
- Tidak menambah izin berbahaya baru di `AndroidManifest.xml`.
- Berfungsi juga saat app PhishGuard utama belum dibuka sama sekali sebelumnya (cold start dari intent).

## Status

**Selesai** (2026-11-12). Diuji di emulator Android 36 — lihat `plans/2026-11-12-full-testing.md` (baris 7–7e).

## Rencana eksekusi (agent)
1. Toolchain Android: JDK 21 via **apt** (`openjdk-21-jdk-headless`), Android cmdline-tools resmi (zip dl.google.com) → `~/Android/Sdk`,
   lalu `sdkmanager`: platform-tools, platform & build-tools yang diminta Flutter, emulator + system image x86_64 (KVM ada).
2. Prasyarat APK dasar: izin `INTERNET` di manifest utama + izinkan HTTP cleartext (API lokal `http://10.0.2.2:8000` / IP LAN) lewat
   `network_security_config` → `flutter build apk` sukses.
3. Fitur: `ScanTextActivity` (Kotlin, turunan `FlutterActivity`, background transparan) + intent-filter `PROCESS_TEXT`,
   Dart entrypoint terpisah `scanMain()` → ambil teks via MethodChannel → `POST /v1/predict` → dialog hasil (label, confidence, reasons).
   Teks >2000 karakter dipotong + diberi catatan.
4. Verifikasi di emulator headless: `adb shell am start -a android.intent.action.PROCESS_TEXT ...` (cold start) → screenshot dialog;
   `queryIntentActivities` membuktikan PhishGuard terdaftar di menu seleksi teks; cek manifest tidak menambah izin berbahaya.
5. Docs: README (cara build APK & pakai fitur), status plan ini.

## Hasil
- Toolchain: JDK 21 (apt), Android SDK di `~/Android/Sdk` (cmdline-tools resmi, platform 36, build-tools 36.0.0, NDK & CMake diunduh otomatis oleh Gradle), AVD `phishguard_test`.
- Kode: `mobile/android/.../ScanTextActivity.kt`, manifest (activity + intent-filter, izin `INTERNET`, `network_security_config` untuk HTTP lokal), tema `TranslucentTheme`,
  Dart `scanMain()` di `lib/main.dart` + `lib/scan.dart` (popup), widget bersama dipindah ke `lib/widgets.dart`. Hasil scan juga masuk riwayat.
- Kriteria: muncul di menu seleksi teks ✅ (query PROCESS_TEXT) · popup + hasil cold start ±0,7–1,5 s buka (APK release) ✅ · tidak ada izin berbahaya baru ✅ · cold start ✅.
- Keamanan: cleartext HTTP diizinkan hanya karena API kuliah jalan di laptop; untuk produksi pakai HTTPS dan hapus `network_security_config`.
