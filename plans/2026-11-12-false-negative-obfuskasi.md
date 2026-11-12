# Plan: False negative — pesan penipuan dengan obfuskasi karakter lolos deteksi

Tanggal: 2026-11-12 · Status: **selesai — dikerjakan di `plans/2026-11-12-dataset-judol.md`**
Asal: user mencoba sendiri lewat app yang sudah live (`https://phishguard.taile0ea7c.ts.net`) dengan teks nyata:

```
Ke cici01 peener1ma THR 275.000! akaligabandar.mom aambil skrg pkai k0dee : PUASA2026
```

Hasil: **"aman", confidence 0,7455, tidak ada rule yang kena**. Direproduksi lewat `POST /v1/predict` ke
`localhost:8080` (hasil sama) — bukan masalah jaringan/Funnel, murni model + rules tidak mengenali pola ini.

## Analisis akar masalah (baca `api/app/rules.py`)

1. **TLD `.mom` tidak ada di `TLDS`** (daftar TLD yang dikenali regex `DOMAIN`) — jadi `akaligabandar.mom` tidak
   terdeteksi sebagai domain sama sekali, rule domain tidak pernah sempat dievaluasi untuk teks ini.
2. **`_lookalike_domain` cuma untuk brand-mimicry** — hanya menyala kalau token domain beririsan dengan set
   `BRANDS` (bca, bri, dst). `akaligabandar` bukan tiruan brand resmi, jadi di luar scope rule ini walau TLD-nya
   dikenali. Kata "bandar" sendiri istilah umum judi online di Indonesia — sinyal yang relevan tapi tidak ditangkap
   skema brand-mimicry.
3. **Tidak ada rule untuk "klaim hadiah/kode promo"** — rule yang ada: `.apk`, `share_code_request` (minta kode
   **dikirim** ke penipu), `paid_task_job` (kerja dibayar per tugas). Pola "pakai/klaim kode ini untuk ambil
   hadiah sekarang" adalah intent berbeda, belum ada rule-nya sama sekali.
4. **Obfuskasi karakter mengelabui model ML**: `peener1ma` (penerima), `pkai` (pakai), `k0dee` (kode), `aambil`
   (ambil) — substitusi huruf↔angka dan pengulangan/penghilangan huruf membuat token-token ini out-of-vocabulary
   untuk TF-IDF yang dilatih dari teks bersih. Model kehilangan sinyal kata kunci yang seharusnya menaikkan skor
   phishing. Ini teknik evasion klasik (mirip cara spam email lolos filter kata kunci).

## Kaitan dengan temuan sebelumnya

Melengkapi (bukan menggantikan) temuan "oracle" di `plans/2026-11-12-keamanan-api.md` poin 5: di sana soal
penyerang membaca `reasons` untuk tahu kenapa ketahuan lalu mengubah teksnya. Di sini soal pola evasion yang
sudah efektif *tanpa* perlu membaca `reasons` sama sekali — obfuskasi karakter sederhana sudah cukup mengelabui
baseline model + rules yang ada sekarang. Keduanya layak masuk bagian keamanan/keterbatasan Laporan akhir.

## Opsi perbaikan (belum dipilih — diskusikan prioritas vs. waktu yang tersisa)

1. **Perluas `TLDS`** di `rules.py` dengan TLD generik baru yang sering dipakai domain scam (`.mom`, `.icu`
   sudah ada, tambah yang lain yang relevan) — perbaikan kecil, cepat dikerjakan, tapi tidak menyelesaikan
   masalah utama (rule domain tetap brand-only).
2. **Rule baru: domain + konteks klaim/hadiah** — independen dari `BRANDS`, cukup: ada domain (TLD apa pun
   di `TLDS`) **DAN** kata kunci klaim (`klaim`, `ambil`, `menang`, `hadiah`, `dapat`, `menerima` + nominal
   uang/THR) dalam jarak dekat. Risiko: naikkan false positive untuk promo marketing sah — perlu diuji dengan
   data `data/processed/` kelas aman sebelum dipakai (pola sama seperti rule lain yang sudah ada, 0 false alarm
   jadi syarat).
3. **Normalisasi teks sebelum diproses** (baik untuk rules maupun fitur TF-IDF): map substitusi umum
   (`0→o, 1→i/l, 3→e, @→a`, dsb.) sebelum matching/tokenisasi. Ini pendekatan lebih umum — menutup seluruh
   kelas evasion obfuskasi karakter, bukan cuma kasus ini. Risiko: normalisasi bisa mengubah makna kata sah
   (mis. "Rp1" jadi "Rpl"?) — perlu desain hati-hati, idealnya whitelist konteks atau cuma dipakai untuk deteksi
   rule, bukan mengubah teks yang dikirim ke model/ditampilkan ke user.
4. **Retrain dengan data augmentasi obfuskasi**: tambahkan versi ter-obfuskasi dari contoh training yang ada
   (character substitution augmentation) supaya TF-IDF belajar pola ini juga. Butuh data & waktu training ulang.

Rekomendasi awal: opsi 1 (cepat) + opsi 2 (menutup gap paling jelas dari kasus ini) dulu, uji 0 false-alarm,
opsi 3/4 kalau waktu memungkinkan sebelum UAS — dicatat sebagai keterbatasan di Laporan kalau tidak dikerjakan.

## Kriteria selesai (verify)
- Teks contoh di atas (dan variasi serupa) terdeteksi sebagai phishing.
- Tidak ada regresi: 0 false alarm tetap di seluruh data aman (sama seperti rule lain), 36 pytest tetap lulus.
- Kalau opsi 3 (normalisasi) dikerjakan: teks yang ditampilkan ke user via `reasons`/riwayat tetap teks asli
  (normalisasi cuma internal untuk deteksi), supaya tidak membingungkan.
- Dicatat di README & Laporan (bagian keterbatasan/pengujian) terlepas dari opsi mana yang akhirnya dipilih.

## Catatan review (2026-11-12 14:20)
Diverifikasi ulang terhadap container lokal (`localhost:8080`):
- Teks asli → aman 0,7455, `reasons` kosong (sama dengan temuan). `.mom` memang tidak ada di `TLDS` (`api/app/rules.py:42-43`).
- **Obfuskasi bukan penyebab utama.** Versi bersih ("penerima THR 275.000! akaligabandar.com ambil skrg pakai kode : PUASA2026")
  tetap **aman 0,6409**. Promo judol "Bonus deposit 100% slot gacor, daftar sekarang di akaligabandar.mom" → aman 0,5382.
  Yang kurang adalah cakupan data: di train+test (7.067 pesan) kata `gacor`, `judi`, `.mom` = 0 kemunculan; `slot` 3 (semua aman).
  Model belum pernah melihat pola judi online / klaim THR dari situs judol. Opsi 3 (normalisasi) saja tidak akan membalik kasus ini.
- **Opsi 2 seperti yang ditulis gagal syarat 0 false alarm.** Simulasi "ada domain + kata klaim/ambil/hadiah/menang/thr/bonus/kode" pada data ID:
  7 dari 820 pesan aman ikut kena (kode THR MatahariMall, Domino's `Kode:VR25D`, bonus Telkomsel, promo Indosat), 132 dari 450 phishing kena.
  Promo resmi memang memakai "kode" + link, jadi kata kunci klaim tidak cukup membedakan.
- Rekomendasi: (a) opsi 1 (tambah `mom` dan TLD scam lain yang benar-benar terlihat); (b) rule sempit khusus judi online:
  domain + kosakata judol (`gacor`, `maxwin`, `togel`, `slot`, `rtp`, `bandar`, `depo/wd`), diuji 0 false alarm di seluruh data aman;
  (c) tambahkan contoh judol/klaim-THR asli ke data lalu latih ulang (sejalan dengan rencana "kumpulkan SMS asli");
  (d) normalisasi angka→huruf hanya di dalam pencocokan rule (`k0de`, `peener1ma`), tidak mengubah input model. Opsi 4 (augmentasi) belakangan.
