# PhishGuard — Project AI Kuliah (Kecerdasan Buatan, Kode MK 788, UBSI)

Aplikasi deteksi SMS/Email phishing. Mata kuliah PBL (Project-Based Learning): kerja kelompok (maks 5 orang), membangun aplikasi AI lengkap dari Minggu 1 sampai akhir semester — Flutter UI + REST API + model inference + deployment, dinilai lewat Proposal dan Laporan akhir.

## Status saat ini (per 2026-11-12)

- [x] Studi kasus dipilih: **deteksi SMS/Email phishing** (klasifikasi teks: Phishing / Aman + skor confidence).
- [x] Checkpoint Minggu 1 (bobot RPS 5%) sudah dibuat: `docs/Checkpoint1_PhishGuard_RancanganAwal.docx` (2 halaman) — berisi masalah/pengguna/tujuan, input-output, 3 kebutuhan fungsional, 3 kebutuhan nonfungsional terukur, diagram 5 komponen, mockup Flutter awal.
- [ ] **Belum diisi**: nomor/nama kelompok, kode kelas, nama+NIM anggota tim — isi manual di docx di atas (sengaja dikosongkan, bukan data milik asisten).
- [x] Dataset siap (2026-11-12): `data/processed/` — 6.939 SMS (EN Mendeley smishing + ID Rahmi & Wibisono), phishing ~12%, split train/test 80/20. Detail, lisensi & sitasi: `data/README.md`; rencana: `plans/2026-11-12-dataset.md`.
- [x] Model (2026-11-12, retrain #2 dengan data ID 2021+): TF-IDF (kata + karakter) + Logistic Regression → `model/phishguard.joblib`. Test: **akurasi 97,8%**, F1 phishing 0,921 (EN 0,901 · ID 0,944). Detail: `model/metrics.json`.
- [x] REST API FastAPI (`api/`): `GET /health`, `POST /v1/predict`. 46 tes pytest lulus (termasuk aturan, judol & keamanan) (FR-01, FR-02, NFR-02 teks tidak di-log, NFR-01 latency). Latency HTTP di Docker p95 ≈ 6 ms.
- [x] Lapisan aturan (`api/app/rules.py`): .apk, minta kode OTP, kerja dibayar per like/tugas, domain tiruan brand, situs/promo judi online (2026-11-12). 0 false alarm di 6.089 pesan aman; challenge v2 8/12 → 11/12 (optimis, lihat `plans/2026-11-12-lapisan-aturan.md`). Respon API punya `reasons`, ditampilkan di app.
- [x] Docker: `docker compose up -d --build` → API :8000 + web UI :8080.
- [x] Aplikasi Flutter (`mobile/`): input, validasi kosong, kartu hasil + confidence, riwayat lokal, pengaturan URL server. `flutter analyze` bersih, 9 widget test lulus, diuji end-to-end di Chrome.
- [~] Modus penipuan ID terbaru: ditambah 69 teks penipuan 2022+ (kutipan berita) + bopbi 2021. Challenge v1 1/5 → 5/5; challenge **v2 (unseen) 8/12** — masih lolos kurir/foto-paket APK & lowongan part-time, 1 false alarm notifikasi BCA asli. Perlu SMS asli dari anggota kelompok → `data/raw/indo/kelompok/`. Detail: `plans/2026-11-12-data-indonesia-terbaru.md`.
- [x] APK Android (2026-11-12): `cd mobile && flutter build apk --release` → `build/app/outputs/flutter-apk/app-release.apk`. Diuji di emulator Android 36.
- [x] Fitur **"Scan dengan PhishGuard"** di menu seleksi teks app mana pun (`ACTION_PROCESS_TEXT`, tanpa izin sensitif) — popup hasil + alasan. Lihat `plans/2026-11-12-fitur-scan-text-selection.md`.
- [x] **"Bagikan" ke PhishGuard** (`ACTION_SEND text/plain`) untuk SMS/WhatsApp yang teksnya tidak bisa diblok — popup yang sama (2026-11-12), **diuji di HP Android asli: berhasil**. Lihat `plans/2026-11-12-fitur-share-ke-phishguard.md`.
- [x] **Hardening API** (2026-11-12): rate limit 60 req/menit per IP per worker (2 worker → 429 + `Retry-After`), body maks 32 KB (413, sebelum JSON di-parse, termasuk chunked), CORS hanya origin web (`CORS_ORIGINS`), `--limit-concurrency 64`, keep-alive 5 s. 36 pytest + 9 widget test lulus; diuji live di Docker. Lihat `plans/2026-11-12-keamanan-api.md`.
  Keterbatasan yang sengaja dibiarkan: `confidence` + `reasons` bisa dipakai penyerang sebagai "oracle" untuk mengakali deteksi sedikit demi sedikit (trade-off eksplainabilitas) — **wajib ditulis di bagian keamanan Laporan akhir**.
- [x] Full testing semua lapisan lulus — `plans/2026-11-12-full-testing.md`.
- [x] Draf Proposal (2026-11-12): `docs/Proposal_PhishGuard.docx` — tinggal isi data identitas kelompok (lihat `plans/2026-11-12-proposal.md`).
- [x] Repository Git (2026-11-12): https://github.com/lildwagz/phishguard (publik). Tidak di-push: `materi-kuliah/`, template kosong UBSI, dataset tanpa lisensi (ekaputra, spacegoalex) — lihat `.gitignore`. Commit atas nama `lildwagz` saja (tanpa atribusi AI).
- [~] Draf Laporan (2026-11-12): `docs/Laporan_PhishGuard.docx` (43 hlm, salinan template; sumber `docs/laporan_src/`). Bagian yang belum ada buktinya ditulis jujur sebagai belum dilakukan: live app, stress test Locust, uji pengguna di luar kelompok, tag release, request ID. Lihat `plans/2026-11-12-laporan.md`.
- [x] **Deteksi judi online** (2026-11-12): dataset judol CC BY 4.0 (Ekaputra 2026, 3.861 baris setelah disaring) → **detektor judol terpisah** di bundle model (test judol P 0,976 R 0,933; 0 alarm di 6.089 SMS aman) + aturan `online_gambling` + TLD baru. Model utama sengaja tidak dicampur data judol (menurunkan challenge v1 9/9 → 5/9); 0 label SMS lama berubah. Pesan THR judol dari user kini PHISHING 90%. Lihat `plans/2026-11-12-dataset-judol.md`.
- [x] **Deployment publik** (2026-11-12): nginx di container `web` sekarang meneruskan `/v1/` + `/health` ke API (satu origin, `mobile/nginx.conf`); web memakai origin halaman sebagai alamat API; `RATE_LIMIT_PER_MIN=300` per IP pengunjung (Funnel meneruskan IP asli; API hanya percaya XFF dari nginx/ts-web). 46 pytest + 14 tes Flutter lulus, uji Chrome di :8080 lulus. **Live: https://phishguard.taile0ea7c.ts.net** lewat sidecar Tailscale `ts-web` (profile `public`; nyala `docker compose --profile public up -d`, mati `docker compose stop ts-web`). Diuji dari jaringan luar 2026-11-12. Lihat `plans/2026-11-12-deployment-tailscale-funnel.md`.
- [ ] Belum: stress test Locust (P13), tag release.
- [ ] **False negative ditemukan** (2026-11-12, dari app live): teks obfuskasi (`k0dee`, `pkai`, `peener1ma`) +
  domain TLD `.mom` + pola "klaim hadiah/THR" lolos jadi "aman" (confidence 0,75). Akar masalah & opsi perbaikan:
  `plans/2026-11-12-false-negative-obfuskasi.md`.

## Rencana arsitektur (dari checkpoint 1)

```
Pengguna → Flutter UI → REST API → AI Service (TF-IDF + Logistic Regression + lapisan aturan; NB jadi pembanding)
                                         ↓                    ↓
                                    Data/Log           Deployment + Monitoring
```
Lihat `mockups/arsitektur.png` dan `mockups/mockup_flutter.png` untuk visualnya.

## Kebutuhan yang sudah didefinisikan

**Fungsional:**
- FR-01: input teks pesan → output label + confidence
- FR-02: validasi input kosong
- FR-03 (should): riwayat analisis lokal

**Nonfungsional (terukur):**
- NFR-01: latency prediksi ≤ 3 detik (p95)
- NFR-02: isi pesan tidak disimpan permanen di server (privasi)
- NFR-03 (direvisi 2026-11-12): pada data uji, **akurasi ≥ 85% dan F1 kelas phishing ≥ 0,85**. Akurasi saja tidak cukup karena data tidak seimbang (phishing ±12%, model yang selalu menjawab "aman" sudah dapat ±88%). F1 menggabungkan precision (berapa banyak peringatan yang benar) dan recall (berapa banyak penipuan yang tertangkap). Saat ini: akurasi 0,978 · F1 0,921 ✅ — dicek otomatis di `model/metrics.json` (`nfr03`).

## Struktur folder

```
PhishGuard/
├── README.md                  ← file ini
├── docs/                      ← dokumen akademik (checkpoint, template proposal/laporan UBSI)
├── materi-kuliah/             ← 16 slide PDF Pertemuan 1-16 (materi mata kuliah, referensi metodologi per minggu)
├── mockups/                   ← source image diagram arsitektur & mockup Flutter (PNG)
├── plans/                     ← semua rencana & catatan riset (1 file bertanggal per topik)
├── data/                      ← raw/ (sumber asli, jangan diubah) + processed/ (train/test) + README.md (lisensi, sitasi)
├── src/data/prepare_dataset.py ← bangun ulang data/processed dari data/raw
├── src/model/train.py         ← latih + evaluasi model → model/
├── model/                     ← phishguard.joblib + metrics.json
├── api/                       ← FastAPI (app/main.py), tests/, Dockerfile, requirements.txt
├── mobile/                    ← aplikasi Flutter (lib/main.dart, api.dart, history.dart), Dockerfile.web
├── docker-compose.yml         ← api :8000 + web :8080
├── requirements-dev.txt       ← dependensi Python untuk training & tes (.venv)
└── .claude/skills/            ← skill agent yang terpasang (lihat skills-lock.json)
```

## Cara menjalankan

```bash
# 1) Python (training & tes) — sekali saja
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python src/data/prepare_dataset.py     # data/raw → data/processed
.venv/bin/python src/model/train.py              # → model/phishguard.joblib + metrics.json
(cd api && ../.venv/bin/python -m pytest -q)     # tes API

# 2) Flutter (SDK di ~/development/flutter; tambahkan ke PATH)
export PATH="$HOME/development/flutter/bin:$PATH"
(cd mobile && flutter test && flutter build web --release)

# 3) Jalankan semuanya
docker compose up -d --build                     # API http://localhost:8000/docs · Web http://localhost:8080
```
Android: build APK dulu **tanpa** emulator menyala (RAM 7 GB → OOM), lalu `~/Android/Sdk/emulator/emulator -avd phishguard_test -gpu host -memory 1536`. App default memanggil `http://10.0.2.2:8000`; HP fisik: ubah alamat server lewat ikon ⚙️ ke IP laptop di jaringan yang sama.

## Langkah selanjutnya (belum dikerjakan)

1. **Minta anggota kelompok menulis challenge v3** (±20 pesan, tanpa melihat aturan/model) untuk evaluasi yang adil, dan **kumpulkan SMS/WA asli** (penipuan + notifikasi resmi bank/kurir/OTP, ±100 pesan) ke `data/raw/indo/kelompok/` (lihat README di sana), lalu latih ulang dan cek `data/challenge/challenge_id_v2.csv`.
2. ~~Uji APK di HP sungguhan~~ — sudah (2026-11-12), termasuk menu Bagikan dari SMS.
3. ~~Revisi NFR-03~~ — selesai (akurasi ≥ 85% **dan** F1 phishing ≥ 0,85). Kalau Checkpoint/Proposal sudah dikumpulkan dengan NFR-03 lama, sebutkan revisi ini di Proposal/Laporan.
4. Isi Proposal (`docs/Template_Proposal_…docx`, BAB I–V) — metrik, sitasi dataset, dan arsitektur sudah tersedia.
5. Deployment ke server/cloud + monitoring, lalu Laporan akhir (`docs/Template_Laporan_…docx`).
   Hardening API sudah dikerjakan (`plans/2026-11-12-keamanan-api.md`). Rencana akses publik: Tailscale Funnel
   dari laptop + nginx satu origin (`plans/2026-11-12-deployment-tailscale-funnel.md`, belum dikerjakan).
   Funnel meneruskan IP pengunjung asli (temuan awal "kuota bersama" keliru, lihat plan keamanan bagian "Koreksi");
   API memercayai `X-Forwarded-For` hanya dari 172.28.0.10 (nginx) dan 172.28.0.11 (ts-web).
   Uji beban: naikkan `RATE_LIMIT_PER_MIN` dulu, kalau tidak hasilnya didominasi 429.
6. ~~Fitur "Scan via Text Selection"~~ — selesai, lihat status di atas.

## Catatan penting

- Materi kuliah asli (`materi-kuliah/*.pdf`) adalah bahan bersama semester ini, bukan spesifik PhishGuard — jangan dihapus, berguna untuk cek rubrik/kriteria tiap minggu.
- File asli tugas kuliah (termasuk 2 template Word) awalnya ada di `~/Downloads/788/` — sekarang sudah disalin ke sini; folder Downloads masih ada juga (belum dihapus).
