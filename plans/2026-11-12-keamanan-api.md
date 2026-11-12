# Plan: Keamanan API (`api/`) — hardening sebelum publik

Tanggal: 2026-11-12 · Status: **selesai (2026-11-12)** — lihat bagian Hasil di bawah
Konteks: user bertanya "api kita bisa diabuse ga sih?" — review kode `api/app/main.py`, `api/app/rules.py`,
`docker-compose.yml`, `api/Dockerfile`. Jadi lebih penting kalau rencana deployment via **Tailscale Funnel**
(lihat `plans/2026-11-12-deployment-tailscale-funnel.md`) jalan — API akan punya URL publik di internet, bukan cuma LAN/emulator.

## Temuan

1. **Tidak ada rate limiting / auth** — `POST /v1/predict` terbuka tanpa API key atau pembatasan per-IP.
   Begitu di-funnel ke publik, siapa pun bisa spam request.
2. **CORS `allow_origins=["*"]`** (`main.py`) — situs manapun bisa panggil API ini dari browser pengunjungnya.
   Tidak pakai cookie/credential jadi risiko CSRF klasik rendah, tapi dikombinasikan dengan poin 1 bisa jadi
   vektor amplifikasi (browser pengunjung situs lain dipakai diam-diam untuk membanjiri API kita).
3. **Tidak ada limit ukuran body di level Uvicorn/FastAPI** — `max_length=2000` di Pydantic baru dicek
   *setelah* JSON di-parse. Body besar (ratusan MB) tetap diproses parser dulu → vektor DoS memori/CPU.
4. **Single worker, tanpa reverse proxy/timeout** — `CMD uvicorn ...` tanpa `--workers`, default 1 proses.
   Beberapa koneksi lambat/paralel bisa membuat service antre (slowloris-style), tidak ada timeout di depannya.
5. **API jadi "oracle" untuk menyempurnakan phishing** — respons `/v1/predict` mengembalikan `confidence`
   **dan** `reasons` (rule mana yang kena, mis. ".apk" atau "domain mirip brand"). Siapa pun bisa iterasi:
   kirim teks, baca alasan, modifikasi teks sedikit demi sedikit sampai lolos deteksi. Ini bukan bug kode,
   tapi trade-off eksplainabilitas vs. robustness yang melekat pada desainnya — tidak realistis "diperbaiki"
   tanpa menghilangkan fitur `reasons` yang justru dipakai di UI. Perlu didokumentasikan sebagai limitation,
   bukan dihilangkan.
6. **Minor**: `GET /health` membocorkan `model_version` — risiko rendah, sekadar fingerprinting.

## Perbaikan yang disarankan (urutan prioritas, sebelum benar-benar publik)

1. **Rate limiting** — paling penting. Opsi: `slowapi` (middleware FastAPI, per-IP) atau `limit_req` di nginx
   kalau nanti ada reverse proxy di depan (lihat plan Tailscale Funnel — nginx reverse-proxy sudah disebut
   di sana untuk alasan lain, jadi `limit_req` bisa ditambah di konfigurasi yang sama).
2. **Batas ukuran body** — middleware FastAPI yang menolak request dengan `Content-Length` di atas batas
   wajar (mis. 10 KB — jauh lebih dari cukup untuk teks 2000 karakter + overhead JSON) **sebelum** body
   dibaca/diparse.
3. **CORS dibatasi** — ganti `allow_origins=["*"]` jadi daftar origin yang benar dipakai (domain web app,
   `http://localhost:8080` untuk dev). Tidak menghilangkan fungsi apa pun karena app tidak pernah memanggil
   dari origin lain.
4. **Worker count & timeout** — `uvicorn --workers <n>` (sesuaikan jumlah core laptop) di `Dockerfile`/compose,
   atau pindahkan ke `gunicorn -k uvicorn.workers.UvicornWorker` dengan `--timeout`. Kalau nginx reverse-proxy
   sudah ada (plan Funnel), tambahkan juga `proxy_read_timeout` di sana.
5. **Dokumentasi, bukan kode**: tulis poin 5 (oracle untuk evasion) sebagai known limitation di bagian
   keamanan Laporan akhir — jelaskan trade-off-nya, jangan hapus `reasons` dari respons.
6. **Opsional**: `GET /health` cukup kembalikan `{"status": "ok"}` tanpa `model_version` kalau API publik;
   untuk debugging internal, `model_version` tetap berguna — bisa taruh di endpoint terpisah yang tidak di-funnel.

## Dependensi / urutan kerja

- Tidak mengubah model/rules — murni perubahan di `api/` (middleware, config) dan `docker-compose.yml`/`Dockerfile`.
- Idealnya dikerjakan **sebelum** atau bersamaan dengan plan Tailscale Funnel (deployment publik), karena
  tanpa rate limiting, API yang di-funnel langsung jadi API yang abusable 24/7 dari internet.
- Setelah perubahan: tambah test di `api/tests/` untuk body-size limit & CORS origin yang ditolak; update
  README (checklist + bagian keamanan).

## Kriteria selesai (verify)

- Request bertubi-tubi dari satu sumber mendapat `429 Too Many Requests` setelah ambang tertentu.
- Body JSON berukuran besar (>10 KB) ditolak sebelum diparse penuh (`413 Payload Too Large` atau serupa).
- Request `fetch()` dari origin yang tidak diizinkan ditolak oleh CORS (dicek lewat browser devtools/Playwright).
- `flutter build web` / app yang sudah ada tetap berfungsi normal setelah CORS dibatasi (tidak regresi FR-01).
- README & Laporan menyebutkan limitation poin 5 (oracle/evasion) secara eksplisit.

## Hasil (2026-11-12)

Implementasi tanpa dependensi baru (`slowapi` tidak dipakai): middleware ASGI di `api/app/security.py`.

| # | Perbaikan | Implementasi | Bukti |
|---|---|---|---|
| 1 | Rate limiting | `RateLimit` + `FixedWindowLimiter`, hanya `POST /v1/predict`, per IP klien, `RATE_LIMIT_PER_MIN` (default 60). Dict IP dibatasi 10.000 kunci (dibersihkan saat penuh) | `test_rate_limit_returns_429_with_retry_after`; live: 150 request → 120×200, 30×429 (2 worker × 60), `retry-after: 59` |
| 2 | Batas body | `BodySizeLimit`: tolak `Content-Length` > `MAX_BODY_BYTES` (32 KB) langsung; tanpa/bohong Content-Length → body dibaca maks 32 KB lalu 413. 32 KB dipilih karena 2000 emoji ter-escape `\uXXXX\uXXXX` ≈ 24 KB | `test_body_over_limit_rejected_413`, `test_chunked_body_over_limit_rejected_413`, `test_max_length_emoji_text_still_fits`; live: 40 KB biasa & chunked → 413 |
| 3 | CORS | `CORS_ORIGINS` (default `http://localhost:8080,http://127.0.0.1:8080`), `allow_headers=["content-type"]` | `test_cors_*`; live: preflight `https://evil.example` → 400 tanpa ACAO, `localhost:8080` → 200 |
| 4 | Worker & timeout | Dockerfile: `--workers 2 --limit-concurrency 64 --timeout-keep-alive 5` | container `healthy`, web :8080 → 200 |
| 5 | Oracle/evasion | Tidak diubah (sesuai plan). Dicatat di README sebagai keterbatasan; **wajib masuk bagian keamanan Laporan akhir** (laporan belum dibuat) | README |
| 6 | `/health` tanpa `model_version` | **Tidak dikerjakan**: `model_version` toh ada di setiap respons `/v1/predict` (dibutuhkan untuk monitoring, materi P7), jadi menyembunyikannya di `/health` tidak mengurangi fingerprinting | — |

Tambahan:
- Flutter (`mobile/lib/api.dart`): pesan ramah untuk 429 ("Terlalu banyak permintaan…") dan 413; widget test baru. APK & web di-build ulang.
- `api/tests/conftest.py` menaikkan limit untuk tes latency (100 request); limit asli diuji dengan limiter kecil.
- Catatan deploy: di belakang proxy set `FORWARDED_ALLOW_IPS` (uvicorn) ke IP proxy, kalau tidak semua klien berbagi satu kuota. Limit per worker, jadi efektif ≤ 2× nilai env.
- Uji beban P13 harus menaikkan `RATE_LIMIT_PER_MIN`, kalau tidak hasilnya 429.
- Belum diverifikasi lewat browser sungguhan (Playwright/devtools); CORS dicek lewat preflight curl + TestClient.

## Temuan tambahan (2026-11-12, setelah tes langsung): Tailscale Funnel TIDAK meneruskan IP klien asli

Dites empiris: `tailscale serve` (test echo server lokal) → diakses dari agent yang benar-benar eksternal lewat
`tailscale funnel` ke URL publik. Hasil header yang diterima backend:

```
"X-Forwarded-For": "100.123.90.35"   ← IP tailnet node kita sendiri, BUKAN IP pengunjung eksternal
```

Konfirmasi dari dokumentasi resmi Tailscale: IP klien asli hanya didokumentasikan untuk mode **TCP mentah**
(`--tls-terminated-tcp` + PROXY protocol v1/v2). Untuk mode **HTTP reverse-proxy** (yang dipakai FastAPI/nginx
kita), tidak ada mekanisme resmi untuk mendapatkan IP pengunjung asli — `X-Forwarded-For` yang disuntikkan
tailscaled berisi alamat node kita sendiri, bukan alamat pengunjung.

**Dampak ke hardening di atas**: catatan `FORWARDED_ALLOW_IPS` yang ditulis sebelumnya **tidak cukup** —
mengarahkan uvicorn untuk percaya header `X-Forwarded-For` dari proxy tidak membantu kalau header itu sendiri
salah (selalu sama untuk semua pengunjung). Begitu di-funnel ke publik:
- Rate limit per-IP (`RATE_LIMIT_PER_MIN`) **berubah jadi kuota global** untuk seluruh pengunjung internet,
  bukan per-pengunjung — satu orang spam bisa menghabiskan kuota untuk semua orang yang akses sah di saat
  bersamaan.
- `429`/`Retry-After` tetap berfungsi sebagai pengaman DoS (baik untuk melindungi server), tapi bukan lagi
  "pembatasan per-pengunjung" seperti desain awal.

**Opsi mitigasi (belum dipilih, didiskusikan dengan user)**:
1. Terima sebagai keterbatasan yang didokumentasikan — wajar untuk skala tugas kuliah/demo, bukan servis
   produksi dengan trafik tinggi. Naikkan `RATE_LIMIT_PER_MIN` ke nilai yang masih aman sebagai kuota global
   (bukan per-IP) dan tulis ini secara eksplisit di bagian keamanan Laporan akhir.
2. Pakai mode TCP + PROXY protocol (`tailscale funnel --tls-terminated-tcp=443` + `--proxy-protocol=2`) kalau
   mau IP asli — tapi ini berarti TLS di-terminate di sisi app sendiri (bukan tailscaled), jadi butuh sertifikat
   TLS sendiri di container `api`/`web`, kerja tambahan yang cukup besar untuk tugas kuliah ini.
3. Minimal: funnel hanya dinyalakan saat dibutuhkan (demo/penilaian), tidak 24/7 — mengurangi jendela waktu
   abuse tanpa mengubah kode apa pun (lihat diskusi deployment Tailscale Funnel terpisah).

Belum ada keputusan final — perlu dibahas bersama rencana deployment Funnel sebelum benar-benar dipasang publik.

### Catatan review (2026-11-12 12:30)
- Diperiksa di mesin ini (`tailscale` 1.104.5): flag `--tls-terminated-tcp` dan `--proxy-protocol` (1/2) memang ada di `tailscale funnel`.
- Koreksi opsi 2: dengan `--tls-terminated-tcp`, TLS **di-terminate oleh tailscaled**, lalu TCP polos diteruskan ke app.
  Jadi app tidak perlu sertifikat sendiri. Yang dibutuhkan: penerima yang bisa membaca PROXY protocol. Uvicorn tidak bisa,
  nginx bisa (`listen ... proxy_protocol;` + `set_real_ip_from` + `real_ip_header proxy_protocol;`), lalu nginx meneruskan
  `X-Forwarded-For $proxy_protocol_addr` ke `api` dan uvicorn diberi `FORWARDED_ALLOW_IPS=<IP container nginx>`.
  Container `web` sudah memakai nginx, jadi kerjanya lebih kecil dari perkiraan, walau tetap perlu diuji.
- Tanpa perubahan apa pun, semua pengunjung lewat `tailscale serve` → `localhost:8000` sudah terlihat dari satu alamat
  peer (localhost/gateway Docker), dan uvicorn tidak memercayai XFF. Akibatnya kuota sudah global sejak sekarang, terlepas dari isi XFF.
- Kapasitas: p50 3,9 ms per request (laporan 5.3), jadi 2 worker sanggup jauh di atas 120 request/menit. Kuota global 120/menit
  lebih mungkin menolak pengguna sah (misalnya saat penilaian di kelas, ±30 orang mencoba bersamaan) daripada melindungi CPU.
- Rekomendasi: opsi 1 + 3 untuk demo. Naikkan ke ±300/menit per worker sebagai kuota global, nyalakan Funnel hanya saat demo,
  dan tulis keterbatasannya di Laporan BAB VI. Opsi 2 dikerjakan hanya kalau sempat sebelum UAS.

## Koreksi temuan Funnel (2026-11-12 14:10): IP pengunjung asli MEMANG diteruskan
Bagian "Temuan tambahan" di atas **keliru**. Bukti dari log nginx setelah sidecar `ts-web` live:
- curl dari laptop lewat DNS publik → XFF `180.252.94.138` (IP publik rumah); agen fetch eksternal → `81.171.74.60`; bot internet → IP masing-masing;
  APK di HP → IPv6 publik HP. Hanya Chrome di laptop yang lewat tailnet (MagicDNS) tercatat `100.123.90.35`.
- Jadi `100.123.90.35` di uji awal adalah alamat tailnet **pengirim** (request lewat tailnet), bukan "alamat node kita sendiri untuk semua pengunjung".
- Header palsu `X-Forwarded-For: 6.6.6.6` dari klien publik **dibuang** Tailscale (yang tercatat tetap IP asli).

Perbaikan (`docker-compose.yml`): subnet compose dikunci `172.28.0.0/24`, `web` = 172.28.0.10, `ts-web` = 172.28.0.11,
`FORWARDED_ALLOW_IPS="172.28.0.10,172.28.0.11"` (uvicorn 0.54 membaca XFF dari kanan, ambil alamat pertama yang tidak dipercaya).
Percobaan pertama dengan seluruh subnet `/24` ditolak: gateway 172.28.0.1 ikut dipercaya sehingga `localhost:8080` + XFF palsu → API membaca `7.7.7.7`.
`RATE_LIMIT_PER_MIN` sekarang `${RATE_LIMIT_PER_MIN:-300}` (bisa di-override saat uji).

Bukti setelah perbaikan (log uvicorn): publik + XFF palsu → `180.252.94.138`; `localhost:8080` + XFF palsu → `172.28.0.1`; `192.168.100.14:8080` + XFF palsu →
`192.168.100.14`; `localhost:8000` + XFF palsu → `172.28.0.1`. Dengan `RATE_LIMIT_PER_MIN=5`: IP publik 10×200 lalu 4×429, IP LAN setelahnya 3×200
→ **rate limit per pengunjung berfungsi di belakang Funnel**. Batas dikembalikan ke 300; 36 pytest lulus.
Opsi mitigasi 1–3 di atas dan catatan PROXY protocol di "Catatan review" tidak diperlukan lagi.
