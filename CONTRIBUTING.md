# Panduan Kontribusi PhishGuard

Setiap tugas dicatat sebagai GitHub Issue dan di-assign ke anggota sesuai perannya. Komentar, centang checklist, commit,
dan pull request di issue itu menjadi **bukti kontribusi** di laporan, jadi kerjakan semuanya dari akun GitHub sendiri.

Daftar tugas: https://github.com/lildwagz/phishguard/issues
Tugas milik sendiri: buka daftar issue lalu filter `assignee:<username-anda>`.

## Aturan umum
- **Jangan pernah** menulis nama lengkap, NIM, nomor HP, nomor rekening, atau isi `.env` di repository, issue, atau komentar.
  Data pesan asli wajib disamarkan dulu (contoh: `08xx-xxxx`, `[NAMA]`, `[REKENING]`).
- Satu issue untuk satu tugas. Kalau menemukan masalah baru, buat issue baru, jangan menumpuk di issue lain.
- Dokumen akademik (proposal, laporan, slide) disimpan di Google Drive kelompok, bukan di repository.

## A. Issue tanpa kode (desain, QA, dokumentasi)
Semua dikerjakan langsung di halaman issue.

1. Buka issue-nya, lalu tulis komentar "Mulai dikerjakan".
2. Centang butir checklist di deskripsi issue setiap kali satu butir selesai (bisa diklik langsung).
3. Laporkan progres lewat komentar: hasil uji, link Figma (akses view), screenshot, atau file. File bisa di-drag ke kotak komentar.
4. Menemukan bug: klik **New issue**, beri label `bug`, isi dengan format di bawah, lalu tulis nomornya di issue asal (misal "lihat #12").
5. Selesai: tulis komentar ringkasan hasil, lalu klik **Close issue**.

Format laporan bug:
```
Judul: [singkat, misal "Popup scan tidak muncul dari WhatsApp"]
Perangkat: [HP, versi Android / browser]
Langkah: 1. ... 2. ... 3. ...
Harapan: ...
Kenyataan: ...
Bukti: [screenshot/rekaman layar; samarkan data pribadi]
Seberapa sering: [selalu / kadang / sekali]
```

Checklist QA lengkap ada di [`tests/QA_CHECKLIST.md`](tests/QA_CHECKLIST.md).

## B. Issue yang mengubah kode atau data
### Persiapan (sekali saja)
```bash
git clone https://github.com/lildwagz/phishguard.git
cd phishguard
git config user.name "username-github-anda"
git config user.email "username-github-anda@users.noreply.github.com"
```
Pakai email `noreply` di atas agar email pribadi tidak ikut tercatat di commit publik.

Lingkungan Python dan Flutter (perintah lengkap ada di README):
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
```

### Setiap mengerjakan satu issue (contoh issue #1)
```bash
git checkout main
git pull                                   # ambil versi terbaru
git checkout -b issue-1-data-kelompok      # satu branch untuk satu issue

# ... kerjakan perubahan ...

git add data/raw/indo/kelompok/sms_asli.csv
git commit -m "Tambah 50 SMS penipuan asli (disamarkan), refs #1"
git push -u origin issue-1-data-kelompok
```

Lalu di GitHub:
1. Klik **Compare & pull request** yang muncul di halaman repository.
2. Di deskripsi pull request tulis `Closes #1` dan ringkasan perubahan.
3. Pilih `lildwagz` sebagai **Reviewer**.
4. Setelah di-review dan di-merge, issue #1 tertutup otomatis.

### Sebelum push
- Mengubah API (`api/`): `cd api && ../.venv/bin/python -m pytest -q`, semua harus lulus.
- Mengubah aplikasi (`mobile/`): `cd mobile && flutter test`.
- Mengubah data atau model: jalankan `src/data/prepare_dataset.py` dan `src/model/train.py`, lalu tulis metrik sebelum/sesudah di komentar issue.
- Jangan commit langsung ke `main`, dan jangan commit file `.env`, file kunci, atau data mentah tanpa lisensi.

### Arti kata kunci di commit dan pull request
- `refs #1`: menautkan commit ke issue #1 (issue tetap terbuka).
- `Closes #1`: menutup issue #1 saat pull request di-merge ke `main`.

## Untuk ketua / reviewer
- Pantau semua tugas di tab **Issues**, filter per anggota dengan `assignee:<username>`.
- Review pull request di tab **Pull requests**: cek tes lulus, tidak ada data pribadi, perubahan sesuai issue.
- Bukti kontribusi untuk laporan (Lampiran F): https://github.com/lildwagz/phishguard/issues?q=is%3Aclosed
