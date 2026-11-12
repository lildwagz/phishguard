# judol_0xrafie — Indonesian Online Gambling Promotion Multimodal Dataset

- Ekaputra, D. R. (2026). *Indonesian Online Gambling Promotion Multimodal Dataset* [Data set]. Hugging Face.
  https://huggingface.co/datasets/0xRafie/indonesian-gambling-multimodal-dataset
- Lisensi: CC BY 4.0 (kartu dataset, disalin di `README_hf.md`). Institut Teknologi Sepuluh Nopember.
- Diunduh 2026-11-12, revisi HF `93f00571002bf1bf0dfea67fef68db2a03f0f58a` (lastModified 2026-05-15).
- Hanya `dataset.csv` yang dipakai (kolom `text_caption`, `label`); gambar tidak diunduh.
- `dataset.csv` sha256 `095c1ac2b6eb759022d5a3b7eb673c2a5da918f268b5a58504733c22a2f2a5c8` (2.355.996 byte).

`dataset.csv` **tidak ikut di repository publik** (`.gitignore`) karena memuat nomor telepon (25 baris) dan username
akun media sosial. Untuk membuat ulang `data/processed/`:

```bash
curl -L -o data/raw/indo/judol_0xrafie/dataset.csv \
  https://huggingface.co/datasets/0xRafie/indonesian-gambling-multimodal-dataset/resolve/93f00571002bf1bf0dfea67fef68db2a03f0f58a/dataset.csv
sha256sum data/raw/indo/judol_0xrafie/dataset.csv   # harus sama dengan di atas
```
