# Plan: Request ID (issue #8)

Tanggal: 2026-11-16 · Status: **selesai**
Permintaan user: "ya kerjakan request id, terus commit push untuk issue 8".
Tujuan: satu request bisa ditelusuri dari response sampai baris log, tanpa mencatat isi pesan (NFR privasi tetap).

## Desain
- Middleware ASGI `RequestId` di `api/app/security.py`, dipasang paling luar, sehingga jawaban 413/429/422/500 juga membawa ID.
- ID: pakai header masuk `X-Request-ID` bila cocok `^[A-Za-z0-9-]{8,64}$`; selain itu buat baru (`uuid4().hex`, 32 karakter).
  Validasi mencegah log injection (baris baru, teks panjang) dari klien yang memanggil :8000 langsung.
- nginx (`mobile/nginx.conf`) mengirim `X-Request-ID $request_id` ke API, sehingga nilai dari pengunjung publik selalu diganti ID buatan nginx.
- Response: header `X-Request-ID`. Disimpan di `contextvars`, dicatat di baris log `predict id=...`.
- CORS: `expose_headers=["X-Request-ID"]` agar web dari origin lain (dev) bisa membacanya; di produksi sudah satu origin.
- Di luar cakupan: menampilkan ID di aplikasi Flutter (perlu build APK baru); dicatat sebagai lanjutan.

## Langkah (TDD)
1. Tes gagal dulu di `api/tests/test_security.py`: header ada dan unik; ID masuk yang valid dipakai ulang; ID tidak valid (baris baru, terlalu panjang, karakter aneh) diganti;
   log `predict` memuat `id=<ID>` dan tetap tanpa isi pesan; 413 dan 429 juga membawa header.
2. Implementasi, 47+ pytest lulus.
3. nginx + rebuild container; uji live :8000, :8080, URL publik (header ada, log cocok, spoof lewat nginx diganti).
4. Laporan 4.2, 6.2, 7.2/7.3, ringkasan; README; tutup issue #8 lewat commit `Closes #8`; push.

## Hasil
- TDD: 11 tes baru di `api/tests/test_security.py` gagal dulu (11 failed), lalu lulus. Tes lama `test_message_text_not_logged` disesuaikan ke format log baru
  (`predict id=... len=...`). Total **58 pytest** lulus; 14 tes Flutter lulus (aplikasi tidak berubah).
- Live setelah rebuild api + web: :8000 → ID baru 32 hex; :8000 dengan `X-Request-ID` buatan sendiri yang valid (format `qa-...-0001`) → dipakai ulang;
  :8080 dengan header palsu → diganti ID nginx, dan ID itu sama dengan baris log `predict id=...`; /health juga membawa ID;
  URL publik → HTTP/2 200 + `x-request-id`. 11/11 kasus publik benar, 413/422 tetap, rate limit 300.
- Laporan: 4.2, 6.2, T-16, 7.2, 7.3, jumlah tes. Lanjutan: tampilkan ID di kartu hasil aplikasi (butuh build APK).
