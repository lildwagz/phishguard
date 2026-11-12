# Plan: "Bagikan ke PhishGuard" (ACTION_SEND) — 2026-11-12

Status: **selesai (2026-11-12)** — diuji user di HP Android asli: berhasil
Masalah (uji user di HP asli): di aplikasi SMS/WhatsApp teks pesan tidak bisa diblok, jadi menu
"Scan dengan PhishGuard" (ACTION_PROCESS_TEXT) tidak muncul. Aplikasi SMS punya menu Bagikan/Teruskan.

## Langkah
1. `AndroidManifest.xml`: tambah intent-filter `android.intent.action.SEND` + `text/plain` di `ScanTextActivity` (popup yang sama).
2. `ScanTextActivity.kt`: `getText` membaca `EXTRA_PROCESS_TEXT`, kalau kosong `EXTRA_TEXT` (Share). Dart tidak berubah.
3. `flutter test` + build APK release (`nice -n 19`, emulator mati), lalu `./gradlew --stop`.
4. Cek manifest di APK (aapt dump) memuat SEND.
5. Update README checklist.

Tanpa izin baru: user sendiri memilih PhishGuard di lembar Bagikan.

## Hasil
- `flutter test`: 8/8 lulus. APK release dibangun ulang (51,3 MB, 2026-11-12 09:31).
- `aapt2 dump xmltree` APK: intent-filter `android.intent.action.SEND` ada di ScanTextActivity.
- Diuji user di HP Android asli (2026-11-12): bagikan SMS → popup hasil muncul. Merek HP/aplikasi SMS tidak dicatat.
- Screenshot `mockups/screenshots/android_6_share_popup.png` (emulator, 2026-11-12): SMS kurir J&T (kutipan dari `data/raw/indo/curated_2022plus/kurir_apk.jsonl`) dikirim ke emulator lewat `adb emu sms send`, percakapan dibuka di Google Messages,
  lalu intent `ACTION_SEND text/plain` dikirim **lewat `adb shell am start`** (intent yang sama dengan menu Bagikan). Long-press di Messages tidak dipakai karena emulator mati kehabisan RAM saat dicoba.
  Hasil: PHISHING 95,7%. Jalur lewat lembar Bagikan sungguhan sudah diuji user di HP asli.
  Dipakai sebagai panel (f) Gambar 3.2 proposal (`mockups/ui_android_v2.png`, sumber `ui_android_v2.html`).
