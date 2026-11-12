# SMS/WA asli dari anggota kelompok

Cara menyumbang data (paling berguna untuk memperbaiki model):
1. Salin `template.csv` → `nama_anda.csv` di folder ini.
2. Isi satu pesan per baris, kolom: `text,label,modus`
   - `label`: `phishing` (penipuan) atau `aman` (pesan resmi/normal — **terutama notifikasi bank, OTP, kurir, e-wallet yang asli**).
   - `modus`: bebas, mis. `kurir_apk`, `lowongan`, `otp_resmi`, `transaksi_bank`.
3. **Privasi**: ganti nama orang & nomor HP pribadi dengan `xxx` / `08xxxxxxxxxx`. Jangan masukkan kode OTP yang masih berlaku.
4. Jalankan ulang `src/data/prepare_dataset.py` lalu `src/model/train.py`.

Teks di dalam tanda kutip ganda kalau mengandung koma atau baris baru (Excel/Sheets "Download as CSV" otomatis melakukannya).
