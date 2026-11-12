# Plan: Deployment publik lewat Tailscale Funnel (laptop sendiri)

Tanggal: 2026-11-12 · Status: **selesai: live di https://phishguard.taile0ea7c.ts.net (sidecar ts-web)**
Asal: diskusi di sesi lain (2026-11-11 19:28): "deployment rencana mau di laptop ini sih, tapi pake tailscale mungkin
untuk akses publicnya?". Dipisah dari `plans/2026-11-12-keamanan-api.md`, yang sudah membahas hardening dan temuan IP klien.

## Kondisi sekarang (dicek 2026-11-12)
- Tailscale 1.104.5 aktif, node `zam` (100.123.90.35), domain tailnet `zam.taile0ea7c.ts.net`. `tailscale funnel status` → "No serve config".
- Docker Compose: `api` di :8000, `web` (nginx 1.27-alpine, hanya file statis Flutter web) di :8080.
- Flutter web memanggil API di `http://localhost:8000` (`mobile/lib/api.dart` `defaultBaseUrl()`). Kalau dibuka dari perangkat lain,
  `localhost` mengarah ke perangkat itu sendiri, jadi API gagal dipanggil. Ini harus diperbaiki sebelum Funnel berguna.
- Hardening API sudah ada (rate limit, batas body, CORS). Di belakang Funnel, rate limit berlaku sebagai kuota bersama
  untuk semua pengunjung (lihat plan keamanan, bagian "Temuan tambahan" dan "Catatan review").

## Keputusan desain
1. **Satu origin**: nginx di container `web` meneruskan `/v1/` dan `/health` ke `api:8000`. Web memanggil API
   dengan path relatif (origin yang sama), jadi:
   - cukup satu port yang di-funnel (`https://zam.taile0ea7c.ts.net` → :8080);
   - tidak ada CORS lintas origin di produksi (CORS_ORIGINS tetap untuk dev);
   - port 8000 tidak perlu dibuka ke publik.
   Alternatif dua port (funnel :8443 untuk API) ditolak: dua URL publik, harus menambah origin ke CORS, dan URL API tertanam di build.
2. **APK Android**: alamat server tetap bisa diatur di app. Untuk demo publik isi `https://zam.taile0ea7c.ts.net`.
   Default APK (10.0.2.2) tidak diubah, karena dipakai emulator.
3. **Rate limit**: kuota bersama (opsi 1 di plan keamanan). Usul nilai `RATE_LIMIT_PER_MIN=300` per worker (efektif ≤600/menit),
   karena p50 3,9 ms per request. Angka ini usulan, dikonfirmasi user sebelum dipakai.
4. **Funnel hanya saat demo/penilaian** (opsi 3), tidak 24/7. Laptop juga harus menyala, tidak sleep, dan Docker berjalan.
5. **IP asli (opsi 2, PROXY protocol)**: ditunda, dikerjakan hanya kalau sempat sebelum UAS.

## Langkah
1. `mobile/nginx.conf` baru: `location /` file statis + SPA fallback; `location /v1/` dan `= /health` → `proxy_pass http://api:8000;`
   dengan `client_max_body_size 32k`, `proxy_read_timeout 10s`. Salin di `mobile/Dockerfile.web`.
2. `mobile/lib/api.dart`: di web, default base URL = origin halaman (`Uri.base.origin`). Kalau dibuka dari `flutter run`
   (port bukan 8080), tetap `http://localhost:8000`. Tambah widget/unit test.
3. Build ulang web (`flutter build web --release`), `docker compose up -d --build`, uji `http://localhost:8080` (scan berhasil, /health lewat nginx).
4. Funnel (perlu sudo / operator): `sudo tailscale funnel --bg 8080`. Funnel mengurus sertifikat HTTPS sendiri.
   Matikan setelah demo: `sudo tailscale funnel --https=443 off` (cek dulu sintaks di `tailscale funnel --help` versi terpasang).
5. Uji dari luar tailnet (HP dengan data seluler, Tailscale dimatikan): buka URL, scan 1 SMS phishing + 1 aman,
   kirim body 40 KB → 413, request beruntun → 429.
6. Isi Laporan: URL live app, bukti uji dari luar, keterbatasan (kuota bersama, laptop harus menyala, uptime terbatas),
   dan perbarui README checklist.

## Kriteria selesai
- `https://zam.taile0ea7c.ts.net` terbuka dari jaringan luar tanpa Tailscale, dan prediksi berhasil.
- Port 8000 tidak ter-funnel; `/v1/predict` hanya lewat origin web.
- 36 pytest + widget test tetap lulus; APK tetap bisa memakai IP LAN.
- Laporan BAB VI memuat URL, cara menyalakan/mematikan, dan keterbatasan.

## Risiko
- Laptop sleep / jaringan putus saat penilaian → siapkan video demo cadangan.
- URL memuat nama tailnet; nama itu terlihat publik (bukan rahasia, tetap dicatat).
- Kuota bersama bisa dihabiskan satu orang → 429 untuk semua; diterima untuk skala demo, ditulis di laporan.

## Hasil (2026-11-12, 13:00)
Keputusan user: "kerjakan semuanya" → `RATE_LIMIT_PER_MIN=300` dipakai.

| Langkah | Implementasi | Bukti |
|---|---|---|
| 1 nginx satu origin | `mobile/nginx.conf` (SPA fallback, `/v1/` dan `= /health` → `api:8000`, `client_max_body_size 32k`, timeout 5–10 s, `server_tokens off`), disalin di `mobile/Dockerfile.web`; `.dockerignore` diberi `!mobile/nginx.conf` | `curl :8080/health` → ok; predict .apk → phishing 0,95 + alasan; teks rapat → aman 0,963; 40 KB biasa & chunked → 413 (dari nginx); `{"text":""}` → 422; `/some/route` → 200 (SPA) |
| 2 alamat API web | `baseUrlFor()` di `mobile/lib/api.dart`: Android → 10.0.2.2:8000; web http(s) → origin halaman; localhost port ≠ 8080 (flutter run) → localhost:8000 | TDD: `test/api_url_test.dart` (5 tes) gagal dulu (fungsi belum ada), lalu lulus; total 14 tes Flutter lulus, `flutter analyze` bersih |
| 3 build & uji lokal | `flutter build web --release`, `docker compose up -d --build` | Chrome (Playwright, headless): app menampilkan "Server: http://localhost:8080", scan J&T .apk → PHISHING 95,0%, satu-satunya request ke `http://localhost:8080/v1/predict`; 36 pytest lulus |
| rate limit | `docker-compose.yml` `RATE_LIMIT_PER_MIN: "300"` | 700 request paralel lewat :8080 → 597×200, 103×429, `retry-after` ada |
| 6 laporan/README | Laporan: 2.x, 4.4, 5.2 (T-09 14/14, T-11 baru), 5.4, 6.1, 6.4, 7.3; 39 halaman | `docs/Laporan_PhishGuard_preview.pdf` |

Belum:
- **Langkah 4**: `tailscale funnel --bg 8080` ditolak oleh classifier izin Claude Code (membuka tunnel ingress publik), jadi harus dijalankan user sendiri.
- **Langkah 5**: uji dari luar tailnet, setelah Funnel menyala.
- APK tidak dibangun ulang: perilaku Android tidak berubah (`baseUrlFor(isWeb:false)` tetap 10.0.2.2).

## Revisi: Tailscale per container (sidecar), 2026-11-12 13:20
Permintaan user: "maksud saya itu tailscalenya per container" (bukan `tailscale funnel` di host, yang juga butuh sudo dan ditolak classifier).

- Ruling: hanya container `web` yang diberi sidecar (`ts-web`), karena nginx di `web` sudah meneruskan `/v1/` dan `/health` ke `api`.
  API tidak perlu node sendiri, tidak terbuka ke internet, dan tetap satu origin. Kalau salah, kerugiannya kecil: menambah `ts-api` dengan pola yang sama.
- `docker-compose.yml` service `ts-web`: image `tailscale/tailscale:v1.104.4`, profile `public` (tidak ikut `docker compose up` biasa),
  `TS_HOSTNAME=phishguard`, userspace, state di volume `ts-web-state`, `TS_AUTH_ONCE=true`, `TS_SERVE_CONFIG=/config/serve-web.json`.
- `deploy/tailscale/serve-web.json`: HTTPS :443 → `http://web:80`, `AllowFunnel` untuk `${TS_CERT_DOMAIN}:443`.
- URL yang diharapkan: `https://phishguard.taile0ea7c.ts.net`.
- Dicek: `docker compose config` valid; dari dalam container ts-web, `http://web:80/health` → ok dan `/v1/predict` → phishing 0,9992. Login ke tailnet belum, karena butuh auth key.
- Butuh dari user: auth key (admin console → Settings → Keys → Generate auth key, sekali pakai, tidak ephemeral) di `.env` sebagai `TS_AUTHKEY=...`
  (`.env` sudah di `.gitignore`; jangan ditempel di chat). Tailnet harus mengizinkan HTTPS dan Funnel untuk node tersebut (attr `funnel` di policy).
- Nyala: `docker compose --profile public up -d` · mati: `docker compose stop ts-web` · log: `docker compose logs ts-web`.
- Keterbatasan IP klien tetap sama: serve di sidecar juga meneruskan alamat node, bukan IP pengunjung.

## Hasil langkah 4–5 (2026-11-12, 13:20–13:30)
- User mengisi `TS_AUTHKEY` di `.env`; `docker compose --profile public up -d ts-web` → node `phishguard` (100.80.218.114), `IngressEnabled true`,
  sertifikat ACME untuk `phishguard.taile0ea7c.ts.net` didapat ±37 detik setelah start. Request pertama beberapa detik setelahnya masih gagal (pemanasan).
- Uji lewat DNS publik (1.1.1.1 → 103.84.155.153/.217, `curl --resolve`, jadi tidak lewat tailnet): halaman 200, TLS valid; `/health` ok;
  .apk → phishing 0,95; teks rapat → aman 0,963; 40 KB → 413; teks kosong → 422; :8000 tidak terjangkau; http → 302 ke https.
- Chrome (Playwright, `--host-resolver-rules` ke IP publik): scan "hadiah BCA" → PHISHING 99,8% + alasan domain; satu-satunya request ke `https://phishguard.taile0ea7c.ts.net/v1/predict`; app menampilkan "Server: https://phishguard.taile0ea7c.ts.net".
- Fetch dari luar jaringan ini (agen web-fetch): `/health` 200 dengan body yang sama; `/` 200.
- Throughput lewat Funnel: ±0,8 s per request (koneksi+TLS lewat relay). 700 request paralel 16 → 700×200 (tidak ada 429: tidak pernah mencapai 600/menit).
  800 request paralel 32 → 5 m 23 s, 766×200, 34 gagal koneksi (000). Bottleneck = jalur Funnel, bukan API. Uji beban P13 ke port lokal; hasil Funnel dilaporkan terpisah.
- Laporan: tabel identitas & ringkasan (URL live app), 6.1 (hasil + angka), T-12 baru. 39 halaman.
- Funnel **masih menyala** setelah uji (`restart: unless-stopped`, akan hidup lagi setelah reboot selama container tidak di-stop). Matikan: `docker compose stop ts-web`.

## Koreksi 2026-11-12 14:10
APK di HP asli memakai `https://phishguard.taile0ea7c.ts.net` (user) → request `Dart/3.13` 200 di log nginx.
Log yang sama membuktikan Funnel meneruskan IP pengunjung asli; rate limit sekarang per pengunjung. Detail dan bukti: `plans/2026-11-12-keamanan-api.md`, bagian "Koreksi temuan Funnel".
Catatan: beberapa menit setelah sertifikat terbit, bot internet (pemindai dari log Certificate Transparency) sudah mengakses URL; 4 POST `/v1/predict` dari luar tercatat. Ini wajar untuk URL publik dan alasan Funnel sebaiknya dimatikan di luar demo.
