# Plan: Stress test bertingkat (Laporan 5.4)

Tanggal: 2026-11-14 · Status: **selesai (23.45)**
Permintaan user: "5.4 ini gimana". Template Laporan 5.4 meminta workload, concurrency, duration, p50/p95/p99, throughput,
error rate, resource usage, bottleneck, dan tindakan optimasi. Saat ini 5.4 masih berisi `[hasil stress test]`.

## Desain
- Alat: Locust (venv di scratchpad, tidak masuk requirements proyek). Skrip uji disimpan di repo: `tests/load/locustfile.py`.
- Target: `http://localhost:8080` (nginx → API), jalur yang sama dengan pengunjung publik minus Funnel.
  Funnel tidak diuji beban (bottleneck relay sudah tercatat: ±0,8 s/request, 34/800 gagal pada 32 paralel).
- Workload: `POST /v1/predict` dengan teks acak dari `data/processed/test.csv` (bervariasi panjang dan bahasa), 1 dari 20 request `GET /health`.
  Tiap pengguna virtual menunggu 0,5–1,5 detik antar-request (pengguna membaca hasil), kecuali tingkat terakhir tanpa jeda (kapasitas maksimum).
- Tingkat: 10, 50, 100, 200 pengguna, lalu 100 pengguna tanpa jeda; masing-masing 60 detik setelah spawn selesai.
- Rate limit: semua request dari satu IP, jadi `RATE_LIMIT_PER_MIN` dinaikkan sementara (env override saat `docker compose up -d api`),
  lalu dikembalikan ke 300 dan diverifikasi (429 muncul lagi). Selama ±10 menit uji, URL publik juga tanpa rate limit; diterima.
- Resource: `docker stats` tiap 2 detik untuk api dan web (CPU%, memori); Locust berjalan di laptop yang sama (dicatat sebagai keterbatasan).
- Batas uvicorn: `--limit-concurrency 64` per worker → di atas itu 503. Diharapkan muncul pada 200 pengguna/tanpa jeda; itu temuan, bukan bug uji.

## Kriteria selesai
- Tabel per tingkat: pengguna, durasi, request, RPS, p50/p95/p99, maks, error rate (per kode), CPU/memori api.
- NFR-01 (p95 < 3 detik) dinilai per tingkat. Bottleneck dan tindakan optimasi ditulis berdasarkan data, bukan dugaan.
- Rate limit kembali 300 (terverifikasi), 46 pytest tetap lulus, URL publik tetap jalan.
- Laporan 5.4 dan T-03/lampiran diperbarui, placeholder `[hasil stress test]` hilang.

## Hasil
Data mentah (CSV Locust + docker stats): scratchpad `load/`. Locust 2.47, 60 detik per tingkat, 2 worker, `RATE_LIMIT_PER_MIN=1000000` selama uji.

**Uji 1 (endpoint sync, kode lama)**
| Pengguna | Req | RPS | p50 | p95 | p99 | Error | CPU API |
|---|---|---|---|---|---|---|---|
| 10 | 591 | 10,0 | 9 | 79 | 98 | 0 | 25% |
| 50 | 2.552 | 43,8 | 120 | 390 | 500 | 0 | 160% |
| 100 | 3.974 | 67,2 | 460 | 1.100 | 1.500 | 0 | 208% |
| 200 | 5.354 | 89,8 | 1.500 | 2.000 | 2.400 | 23,1% (1.235×503) | 219% |
| 100 tanpa jeda | 4.179 | 70,6 | 1.500 | 1.800 | 2.000 | 1,7% (503) | 207% |

**Mencari bottleneck** (data, bukan dugaan):
- In-process per pesan: model utama median 1,34 ms (rata-rata 3,67), detektor judol 1,20 ms, aturan 0,03 ms → ±5 ms; API memakai ±22 ms CPU/request (200% / 89,8 rps).
- `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=1` (tiap worker punya 8+8 thread BLAS/OpenMP): 100 pengguna p95 1.000 ms, 200 pengguna 23% 503 → **ditolak**.
- 4 worker: 100 pengguna p95 530 ms, 81,4 rps; 200 pengguna 103,1 rps, 1,4% 503; memori 400 → 655 MiB → membantu sebagian.
- py-spy di container ditolak (tidak ada CAP_SYS_PTRACE), jadi diuji langsung: `def predict` → `async def predict` (patch sementara di container):
  100 pengguna 95,6 rps p95 340 ms; 200 pengguna 199 rps, p95 21 ms, 0 error, CPU 110% → **penyebab: thread pool AnyIO (±40 thread/worker) berebut GIL**.

**Perbaikan**: `api/app/main.py` `health` dan `predict` jadi `async def` (komentar alasan). TDD: `test_endpoints_run_on_event_loop_not_threadpool` gagal dulu, lalu lulus; 47 pytest + 14 Flutter lulus. Image dibangun ulang.

**Uji 2 (final, async)**: memori API maks 310 MiB, 0 error di semua tingkat.
| Pengguna | Req | RPS | p50 | p95 | p99 | Maks | CPU API | CPU nginx |
|---|---|---|---|---|---|---|---|---|
| 10 | 598 | 10,1 | 7 | 11 | 22 | 42 | 6% | 1% |
| 50 | 2.944 | 49,9 | 7 | 11 | 71 | 142 | 25% | 2% |
| 100 | 5.899 | 99,9 | 7 | 12 | 150 | 299 | 51% | 5% |
| 200 | 11.826 | 200,2 | 8 | 20 | 290 | 553 | 113% | 9% |
| 100 tanpa jeda | 19.345 | 327,4 | 300 | 340 | 350 | 417 | 198% | 41% |
| 200 tanpa jeda | 19.087 | 323,3 | 600 | 690 | 700 | 826 | 200% | 48% |

Kapasitas ±325 rps; di atasnya hanya antrean (latency naik linear, throughput tetap). Bottleneck berikutnya: CPU 2 worker. Optimasi berikut bila perlu: worker = jumlah core, rate limit per worker disesuaikan.
NFR-01 terpenuhi di semua tingkat (p95 maks 690 ms).

**Pemulihan**: `docker compose up -d api` → `RATE_LIMIT_PER_MIN=300`; 700 request → 600×200 + 100×429. URL publik `/health` ok.
**Laporan**: 5.4 (uji, bottleneck, tabel hasil), 4.2 (async), 5.6 (kegagalan baru), T-15, 2.4, 7.1–7.3, lampiran D, ringkasan (339 kata). 47 halaman.
Keterbatasan: Locust di laptop yang sama; tanpa jaringan; jalur Funnel tidak diuji beban (bottleneck relay ±0,8 s/request).
