# Plan: Slide UAS dengan skill morph-ppt (gaya Cyber Future)

Tanggal: 2026-11-22 · Status: **selesai; motion belum dicek di WPS/PowerPoint**
Permintaan user: "coba kalo pake skill ppt morph" setelah v3 (academic-pptx) dinilai kurang menarik dibanding slide dokumentasi (issue #11).

## Keputusan
- `officecli` 1.0.163 dipasang manual dari rilis GitHub (sha256 cocok dengan SHA256SUMS) ke `~/.local/bin`, tanpa install.sh
  (skrip itu mengubah .bashrc). Skill `morph-ppt` + dasarnya `officecli-pptx` dipasang di `.claude/skills/` (Apache-2.0, SOURCE.txt).
- Gaya dipilih user dari 3 contoh: `dark--cyber-future` (latar 0B0C10, cyan 66FCF1, teal 45A29E). Font Arial (Montserrat tidak ada).
- Isi = outline v3 yang sudah disetujui; slide 9 dan 10 v3 dipecah jadi dua keyframe (18 slide) agar morph bisa
  menumbuhkan batang F1 (0,19 → 0,83) dan menyusutkan batang latency (2.000 → 20 ms).
- Sumber: `docs/slide_src/morph/brief.md` (outline + tabel pasangan morph) dan `build.py` (docs/ tidak masuk repo).

## Hasil
- `docs/Slide_PhishGuard_morph.pptx` (+ PDF statis cadangan), diunggah ke Drive.
- Gate: `officecli validate` lulus, `view issues` 0, tidak ada token sisa, gambar ber-alt; 17 pasangan morph berbagi ≥ 5 scene actor
  dan ≥ 3 bergerak; tidak ada konten slide N tertinggal di N+1. QA visual lewat render LibreOffice (2 putaran perbaikan:
  teks meluap, titik dekorasi menimpa judul, konektor diganti panah, legenda, label 20 ms).
- Konektor `@name=` gagal di batch (known issue C-P-6); diganti panah bentuk biasa.
- Belum: animasi morph hanya bisa dilihat di WPS/PowerPoint 365; LibreOffice dan PDF statis.
