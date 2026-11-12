# Plan: Lapisan aturan (rules) di samping model — iterasi 2

Tanggal: 2026-11-12 · Status: **selesai**
Alasan: model TF-IDF+LogReg tidak mengenali pola yang tidak ada di data latih (`.apk` = 0 contoh,
lowongan "like video dibayar" ≈ 5 contoh). Lihat `plans/2026-11-12-data-indonesia-terbaru.md`.

## Desain
- `api/app/rules.py`: aturan regex presisi tinggi, masing-masing punya `id`, alasan (bahasa Indonesia), dan skor.
  1. `apk_attachment` — menyebut file `.apk` (modus undangan/foto paket/tilang APK).
  2. `share_code_request` — meminta mengirim/menyebutkan kode OTP/verifikasi/PIN (bukan "JANGAN berikan kode").
  3. `paid_task_job` — tugas like/follow/subscribe + uang/komisi + kerja/paruh waktu.
  4. `lookalike_domain` — domain berisi nama brand (bca, bri, dana, jnt, bpjs, …) tapi bukan domain resmi.
- Keputusan akhir: **phishing jika model ATAU aturan bilang phishing**.
  confidence = max(prob phishing model, skor aturan tertinggi) kalau phishing; prob aman model kalau aman.
- Respon API ditambah `reasons: [..]` (kosong kalau tidak ada aturan terpicu) → ditampilkan di app (explainability).

## Verifikasi
- Unit test per aturan (positif & negatif, termasuk OTP resmi "jangan bagikan kode").
- False alarm aturan pada **semua pesan aman** di train+test (target: ~0, dan dicek manual kalau ada).
- Bandingkan model vs model+aturan di test set & challenge v1/v2.
- pytest API, flutter test, rebuild Docker, cek di browser.

## Hasil (2026-11-12)
- `api/app/rules.py`: 4 aturan (apk_attachment, share_code_request, paid_task_job, lookalike_domain) + allowlist domain resmi.
- Disempurnakan setelah cek false alarm: tambah domain resmi telco/Grab; `pin lokasi` dikecualikan; aturan lowongan butuh *tarif* ("50rb per tugas", "/hari") atau kata komisi/dibayar/upah, bukan sekadar "gaji".
- **False alarm aturan: 0 dari 6.089 pesan aman** (train+test). Aturan memicu di 12 pesan phishing data.
- API: respon ditambah `reasons`; keputusan = model ATAU aturan. Tes: 29 pytest lulus (19 tes aturan positif/negatif, termasuk OTP resmi "jangan bagikan kode").
- Flutter: kartu hasil menampilkan "Tanda bahaya terdeteksi"; 5 widget test lulus; dicek di browser (APK → PHISHING 95% + alasan).

| Set | Model saja | Model + aturan |
|---|---|---|
| Test (1.413) akurasi / F1 phishing | 0,978 / 0,921 | 0,978 / 0,921 (tidak berubah) |
| Challenge v1 (9) | 9/9 | 9/9 |
| Challenge v2 (12) | 8/12 (recall 3/6) | **11/12** (recall 6/6) |

**Catatan jujur:** aturan dirancang *setelah* melihat pesan yang lolos di challenge v2, jadi 11/12 terlalu optimis.
Untuk angka yang adil di Laporan perlu **challenge v3** yang ditulis orang lain (mis. anggota kelompok) tanpa melihat aturan.
Sisa kesalahan v2: notifikasi debit BCA asli tetap dianggap phishing oleh model (aturan tidak bisa mengurangi false alarm).

## Keterbatasan aturan
- Hanya menambah sinyal phishing, tidak pernah mengoreksi false alarm model.
- Penipu bisa menghindar (mis. "a p k", domain tanpa nama brand, shortlink bit.ly).
- Allowlist domain resmi harus dirawat manual.
