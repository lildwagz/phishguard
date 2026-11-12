# -*- coding: utf-8 -*-
# Isi Laporan Project PhishGuard (template UBSI 2026).
# Sumber angka: model/metrics.json, plans/2026-11-12-full-testing.md, plans/2026-11-12-keamanan-api.md,
# plans/2026-11-12-lapisan-aturan.md, plans/2026-11-12-data-indonesia-terbaru.md, pengukuran ulang 12 Nov 2026 (plans/2026-11-12-laporan.md).
# Placeholder [..] = data kelompok atau pekerjaan yang belum dilakukan. Jangan diganti dengan tebakan.

JUDUL = "PhishGuard: Aplikasi Deteksi SMS/Email Phishing"
REPO = "https://github.com/lildwagz/phishguard"
COMMIT = "709179d"

# Nama dan NIM tidak ada di repo publik: diambil dari docs/identitas_kelompok.py (lokal, .gitignore).
# Tanpa file itu dokumen dibuat dengan placeholder.
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
try:
    from identitas_kelompok import KETUA, ANGGOTA
except ImportError:
    KETUA = ("[NIM]", "[Nama Ketua]")
    ANGGOTA = [("[NIM]", f"[Nama Anggota {i}]") for i in range(1, 5)]

IDENTITAS = [
    ("Mata Kuliah", "Kecerdasan Buatan"),
    ("Judul Project", JUDUL),
    ("Kelompok/Kelas", "[Kelompok] / [Kode kelas]"),
    ("Studi Kasus", "Pengguna ponsel sulit membedakan SMS/WhatsApp/email penipuan (phishing) dari pesan resmi sebelum mengklik tautan, memasang file APK, atau menyebutkan kode OTP"),
    ("Platform", "Flutter: Android (APK) dan web"),
    ("Backend/API", "FastAPI (Python 3.14), dikemas Docker"),
    ("Model AI", "Pipeline TF-IDF n-gram kata dan karakter + Logistic Regression (scikit-learn), dilengkapi lapisan aturan"),
    ("Repository", REPO),
    ("Live App", "https://phishguard.taile0ea7c.ts.net (aktif saat demo dan penilaian; lihat subbab 6.1)"),
]

RINGKASAN_META = [
    ("URL Live App", "https://phishguard.taile0ea7c.ts.net (aktif saat demo dan penilaian)"),
    ("URL Repository", f"{REPO} (commit {COMMIT}; tag release belum dibuat)"),
    ("Versi Aplikasi/Model", "API 1.0.0, aplikasi Flutter 1.0.0+1 / model tfidf_logreg-20261112 (model utama + detektor judol)"),
    ("Kata Kunci", "phishing, smishing, klasifikasi teks, Logistic Regression, FastAPI"),
]

S = {}

S["RINGKASAN EKSEKUTIF"] = [
("p", "Penipuan lewat pesan teks masih banyak menimpa masyarakat Indonesia. Indonesia Anti-Scam Centre (IASC) yang dikelola OJK menerima 411.055 laporan penipuan keuangan sejak November 2024 sampai 23 Desember 2025, dengan kerugian yang dilaporkan sekitar Rp9 triliun (Al Hakim, 2026). PhishGuard dibuat agar pengguna ponsel dapat memeriksa SMS, pesan WhatsApp, atau email yang mencurigakan sebelum mengklik tautan, memasang file APK, atau menyebutkan kode OTP."),
("p", "Sistem terdiri dari aplikasi Flutter untuk Android dan web, REST API FastAPI, dan layanan inference. Model berupa pipeline TF-IDF n-gram kata dan karakter dengan Logistic Regression yang dilatih pada 5.654 pesan berbahasa Inggris dan Indonesia dari dataset publik dan kutipan berita penipuan 2022 sampai 2026. Lima aturan regex melengkapi model untuk pola yang tidak ada di data latih, misalnya lampiran .apk, permintaan kode OTP, dan situs judi online, dan alasannya ditampilkan kepada pengguna. Model kedua dengan algoritma yang sama mendeteksi promosi judi online. Di Android, pesan dapat diperiksa dari menu seleksi teks atau menu Bagikan aplikasi lain. API dan web dijalankan dengan Docker Compose. API dilengkapi rate limiting, batas ukuran body, dan CORS terbatas."),
("p", "Pengujian terdiri dari 46 tes pytest, 14 tes Flutter, uji integrasi pada container, uji end-to-end di browser, emulator Android 36, dan HP Android asli, pengukuran latency, serta evaluasi model. Pada 1.413 pesan uji, model mencapai akurasi 97,8% dan F1 kelas phishing 0,921, di atas target 85% dan 0,85. Latency HTTP p95 adalah 8,3 ms pada 55 request ke container lokal, jauh di bawah target 3 detik. Pada 12 pesan modus baru yang ditulis setelah pelatihan, model saja benar 8 dan model dengan aturan benar 11; angka kedua masih optimis karena aturan dibuat setelah melihat pesan yang lolos."),
("p", f"Kode tersedia di {REPO}. Live app tersedia di https://phishguard.taile0ea7c.ts.net lewat Tailscale Funnel dan dinyalakan saat demo. Stress test bertingkat dengan Locust belum dijalankan. Kesimpulannya, prototype sudah memenuhi kebutuhan fungsional dan target kualitas model pada data uji, sedangkan kemampuan mengenali modus baru masih dibatasi oleh sedikitnya data penipuan berbahasa Indonesia terbaru."),
]

S["1.1 Latar Belakang"] = [
("p", "OJK melalui Indonesia Anti-Scam Centre (IASC) mencatat 411.055 laporan penipuan keuangan sejak IASC diluncurkan pada November 2024 sampai 23 Desember 2025. Total kerugian dana yang dilaporkan sebesar Rp9 triliun, dan 681.890 rekening dilaporkan terkait penipuan tersebut (Al Hakim, 2026)."),
("p", "Banyak penipuan dimulai dari pesan teks. Berita cek fakta dan peringatan resmi bank sepanjang 2022 sampai 2025 memuat contoh pesan yang meniru bank, kurir, tagihan PLN dalam bentuk file APK, dan lowongan kerja paruh waktu (Tim Cek Fakta, 2022, 2023; Bank Central Asia, 2025). Pesan seperti ini meniru pengirim resmi, sehingga sulit dibedakan dari notifikasi asli dalam sekali baca."),
("p", "Pengguna biasanya mengandalkan pengalaman sendiri atau berita cek fakta yang terbit setelah suatu modus menyebar. Klasifikasi teks dengan machine learning dapat mempelajari pola kata dari ribuan pesan berlabel dan memberi penilaian dalam hitungan milidetik, sehingga pemeriksaan dapat dilakukan saat pesan diterima. Kebutuhan pengguna yang mendasari project ini adalah jawaban cepat yang mudah dipahami, dapat dipanggil dari aplikasi pesan, dan tidak menyimpan isi pesan pribadi."),
]

S["1.2 Rumusan Masalah"] = [
("p", "Persoalan computing yang diselesaikan adalah klasifikasi teks biner: menentukan apakah sebuah pesan SMS/email termasuk phishing atau aman beserta tingkat keyakinannya, lalu menyajikannya sebagai layanan REST yang dipanggil aplikasi mobile."),
("p", "Pertanyaan evaluasi project:"),
("b", "Apakah model mencapai akurasi minimal 85% dan F1 kelas phishing minimal 0,85 pada data uji yang dipisahkan dari data latih?"),
("b", "Apakah API menolak input tidak valid dengan status yang tepat dan menjawab prediksi dengan latency p95 di bawah 3 detik?"),
("b", "Apakah pengguna dapat memeriksa pesan dari aplikasi Flutter maupun dari aplikasi lain di Android, dan memahami hasilnya?"),
("b", "Seberapa baik sistem mengenali modus penipuan Indonesia yang lebih baru daripada data latih?"),
]

S["1.3 Tujuan dan Kriteria Keberhasilan"] = [
("p", "Tujuan dan indikator keberhasilannya mengikuti kebutuhan pada proposal:"),
("b", "Model klasifikasi: akurasi ≥ 85% dan F1 phishing ≥ 0,85 pada data uji (NFR-05). Diuji dengan model/metrics.json."),
("b", "REST API: GET /health dan POST /v1/predict; input kosong, hanya spasi, atau lebih dari 2.000 karakter dijawab 422 (FR-02); latency p95 < 3 detik (NFR-01). Diuji dengan pytest dan request HTTP ke container."),
("b", "Aplikasi Flutter: menampilkan label, confidence, dan alasan (FR-01, FR-04), menyimpan riwayat lokal (FR-03), dapat dipanggil dari menu seleksi teks (FR-05) dan menu Bagikan (FR-06). Diuji dengan widget test dan uji end-to-end."),
("b", "Keamanan dan privasi: isi pesan tidak disimpan atau dicatat di log, rate limiting, batas ukuran body, dan CORS terbatas (NFR-03). Diuji dengan pytest dan uji langsung pada container."),
("b", "Layanan dapat dijalankan ulang dengan satu perintah Docker Compose dan didokumentasikan di README."),
]

S["1.4 Ruang Lingkup dan Batasan"] = [
("p", "Fitur yang dibangun: klasifikasi biner teks pesan dalam bahasa Indonesia dan Inggris dengan confidence dan alasan, REST API FastAPI, aplikasi Flutter untuk Android dan web, riwayat di perangkat, popup \"Scan dengan PhishGuard\" dari menu seleksi teks dan menu Bagikan Android, serta container Docker untuk API dan web."),
("p", "Di luar ruang lingkup: membaca SMS otomatis di latar belakang (membutuhkan izin SMS), memblokir atau melaporkan pesan, membuka isi tautan atau file APK, menganalisis gambar, dan versi iOS."),
("p", "Data: dataset publik Mishra dan Soni (2022), Rahmi dan Wibisono (2016), bopbi (2021), serta 69 teks penipuan yang dikutip apa adanya dari berita dan peringatan resmi. Data latih berupa pesan singkat, sehingga email panjang belum diuji. Contoh modus Indonesia terbaru masih sedikit."),
("p", "Asumsi: pengguna terhubung ke server API, dan hasil aplikasi dipakai sebagai bantuan awal. Keputusan akhir tetap pada pengguna."),
("p", "Privasi, keamanan, dan etika: isi pesan hanya diproses di memori selama request dan tidak disimpan maupun dicatat di log server. Riwayat disimpan di perangkat pengguna. Aplikasi Android hanya meminta izin INTERNET. Prototype masih memakai HTTP di jaringan lokal. Rinciannya ada di subbab 6.4."),
]

S["2.1 Pengguna, Kebutuhan, dan Skenario"] = [
("p", "Aktor utama adalah pengguna ponsel umum yang menerima pesan mencurigakan dan membutuhkan jawaban cepat dalam bahasa sehari-hari. Aktor kedua adalah pengelola layanan yang memantau kesehatan API, versi model, dan waktu respons."),
("p", "Kebutuhan fungsional dan kriteria penerimaannya:"),
("b", "FR-01 (Must): pengguna memasukkan teks dan sistem menampilkan label Phishing/Aman beserta confidence dalam ≤ 3 detik."),
("b", "FR-02 (Must): input kosong ditolak di aplikasi dengan pesan \"Teks pesan tidak boleh kosong\" tanpa memanggil API; API menjawab 422 untuk teks kosong dan lebih dari 2.000 karakter."),
("b", "FR-03 (Should): setiap hasil tersimpan di riwayat perangkat (cuplikan 80 karakter, label, confidence, waktu), maksimal 50 entri, dapat dihapus."),
("b", "FR-04 (Should): alasan ditampilkan bila pesan berisi file .apk, permintaan kode OTP, kerja dibayar per tugas, atau domain tiruan brand."),
("b", "FR-05 (Could): \"Scan dengan PhishGuard\" muncul di menu seleksi teks Android dan menampilkan popup hasil walaupun aplikasi belum dibuka."),
("b", "FR-06 (Could): \"Scan dengan PhishGuard\" muncul di menu Bagikan untuk teks dan membuka popup yang sama dengan FR-05."),
("p", "Kebutuhan nonfungsional: NFR-01 latency p95 < 3 detik; NFR-02 reliability (request valid dijawab 200, input tidak valid 422, health check, aplikasi tidak crash saat server mati); NFR-03 keamanan dan privasi; NFR-04 usability (keadaan idle, loading, hasil, dan error; label berupa teks dan ikon); NFR-05 akurasi ≥ 85% dan F1 phishing ≥ 0,85."),
("p", "User flow utama: pengguna menyalin pesan, membuka PhishGuard, menempel teks, menekan Analisis, lalu membaca hasil dan alasan. Di Android ada dua jalur cepat. Pada aplikasi yang teksnya dapat diseleksi (Chrome, Gmail), pengguna memilih teks lalu \"Scan dengan PhishGuard\". Pada aplikasi SMS dan WhatsApp, teks pesan tidak dapat diseleksi, sehingga pengguna menekan lama pesan, memilih Bagikan, lalu \"Scan dengan PhishGuard\"."),
]

S["2.2 Data dan Skema Input-Output"] = [
("p", "Sumber data, izin penggunaan, dan pemetaan label:"),
("b", "Mishra dan Soni (2022), Mendeley Data, CC BY 4.0: 5.971 SMS bahasa Inggris berlabel ham, spam, smishing. Smishing dipetakan ke phishing; ham dan spam ke aman."),
("b", "Rahmi dan Wibisono (2016), CC BY-SA 4.0: 1.143 SMS bahasa Indonesia berlabel normal, penipuan, promo. Penipuan dipetakan ke phishing; normal dan promo ke aman. Sitasi dan lisensi mengikuti berkas penjelasan.txt dalam arsip dataset v1.0 (Agustus 2018)."),
("b", "bopbi (2021), CC0 1.0: 48 SMS Indonesia kategori hadiah, pinjaman, promo palsu (phishing) dan SMS premium (aman)."),
("b", "Kutipan 2022 sampai 2026: 69 teks penipuan dan 11 template notifikasi resmi yang dikutip apa adanya dari berita cek fakta dan halaman edukasi bank, masing-masing dengan URL sumber."),
("b", "Ekaputra (2026), CC BY 4.0: caption Facebook, TikTok, dan X berbahasa Indonesia yang dianotasi manual sebagai promosi judi online atau bukan (Ekaputra, 2026). Data ini ditambahkan setelah pesan klaim THR dari situs judol lolos deteksi di live app. Promosi judi online diberi label phishing karena judol ilegal dan situsnya menjadi pintu penipuan, sedangkan posting bukan judol (berita, kampanye anti-judol, konten sehari-hari) diberi label aman."),
("p", "Dua dataset lain (laporan pengguna laporsms.com dan sebuah dataset GitHub tanpa lisensi) diperiksa tetapi tidak dipakai karena tidak berlisensi dan labelnya tercampur. Keduanya juga tidak ikut di repository publik."),
("p", "Preprocessing: normalisasi Unicode NFKC, penyatuan spasi, dan penghapusan duplikat. Sebanyak 34 teks yang muncul dengan label berbeda di sumber berbeda dibuang. Hasilnya 7.067 pesan unik: 6.089 aman dan 978 phishing (13,8%). Data dibagi 80% latih (5.654) dan 20% uji (1.413) secara stratified per label dan sumber dengan seed 42. Menjalankan ulang skrip menghasilkan berkas train.csv dan test.csv yang identik (md5 sama)."),
("p", "Dari 5.028 baris data judol, dibuang baris yang memuat nomor telepon, tautan WhatsApp berisi nomor, atau ID profil Facebook, posting taruhan berbahasa Turki, teks mayoritas non-Latin, teks lebih dari 2.000 karakter, dan teks yang tersisa kurang dari tiga kata setelah tautan, tagar, dan mention dihapus. Username diganti @user. Hasilnya 3.861 baris (1.499 judol, 2.362 bukan judol), dibagi 80/20 dengan pengacak tersendiri sehingga pembagian 5.654 dan 1.413 pesan SMS di atas tidak berubah. Berkas mentahnya tidak ikut di repository publik karena memuat nomor telepon dan username; cara mengunduh ulang dan checksum dicatat di data/raw/indo/judol_0xrafie/SOURCE.md."),
("p", "Validasi tambahan memakai dua challenge set yang tidak pernah dipakai pelatihan: challenge_id.csv (9 pesan) dan challenge_id_v2.csv (12 pesan, ditulis setelah pelatihan ulang)."),
("p", "Bias data: 1.160 dari 1.413 pesan uji (82%) berbahasa Inggris, data Indonesia didominasi modus undian tahun 2016, dan dataset Rahmi mengganti nama orang dengan token \"nama1\". Dampaknya dibahas di subbab 5.5."),
("p", "Skema input-output: input {\"text\": string} wajib, tidak hanya spasi, maksimal 2.000 karakter. Output {label, confidence, model_version, latency_ms, reasons}. Contoh lengkap ada di subbab 3.3."),
]

S["2.3 Pemilihan Model dan Teknologi"] = [
("p", "Model. Dua kandidat dibandingkan dengan fitur yang sama, yaitu TF-IDF n-gram kata (1 sampai 2) digabung n-gram karakter (3 sampai 5). Fitur karakter dipakai karena pesan penipuan sering menyamarkan ejaan. Validasi silang 5-fold pada data latih menghasilkan F1 phishing 0,838 untuk Multinomial Naive Bayes dan 0,919 untuk Logistic Regression dengan class_weight balanced (setelah urutan baris data latih berubah karena penambahan data judol, hasil ulangnya 0,837 dan 0,923; isi data latih dan model akhir tetap sama), sehingga Logistic Regression dipilih (Pedregosa et al., 2011). Bobot koefisien model linear juga dapat dibaca untuk menjelaskan prediksi, sesuai materi XAI Pertemuan 7. Model transformer seperti IndoBERT tidak dipilih karena membutuhkan GPU atau server yang lebih besar, sementara data berlabel Indonesia baru sekitar 1.300 pesan."),
("p", "Lapisan aturan. Token kata \"apk\" tidak ada dalam kosakata kata model karena tidak muncul di data latih, dan kata \"paket\" memiliki bobot -1,15 (condong ke aman) karena sering muncul pada SMS paket internet. Karena itu aturan regex ditambahkan untuk pola yang belum ada di data latih. Saat ini ada lima aturan."),
("p", "Detektor judol. Data judol awalnya dicampur ke data latih model utama, tetapi recall pada modus penipuan Indonesia turun: challenge v1 dari 9/9 menjadi 5/9 dan recall data kurasi 2022 ke atas dari 0,93 menjadi 0,64. Percobaan dengan subsampel dan bobot sampel tetap menurunkan hasil tersebut. Karena itu data judol dipakai untuk model kedua dengan fitur dan algoritma yang sama, yang hanya menjawab apakah sebuah teks adalah promosi judi online. API menandai pesan sebagai phishing bila model utama, detektor judol, atau aturan menandainya. Ambang detektor 0,5, nilai bawaan yang tidak disetel pada data uji."),
("p", "API dan serialization. FastAPI dipilih dibanding Flask karena validasi Pydantic dan dokumentasi /docs tersedia langsung (FastAPI, n.d.). Pipeline disimpan dengan joblib (berbasis Pickle) karena layanan berjalan di lingkungan Python yang sama dengan pelatihan, sehingga tidak perlu konversi ke ONNX."),
("p", "Frontend. Flutter menghasilkan APK Android dan aplikasi web dari satu basis kode (Flutter, n.d.). Streamlit dan Gradio tidak menghasilkan aplikasi Android sehingga tidak dapat terdaftar di menu seleksi teks dan menu Bagikan, yang memakai intent ACTION_PROCESS_TEXT dan ACTION_SEND (Google, n.d.)."),
("p", "Container dan deployment. Docker menjaga versi dependency yang sama di laptop dan server (Docker, n.d.). Untuk akses publik kelompok memilih menjalankan container di laptop pengembang dan membukanya lewat Tailscale Funnel dari container sidecar, yang memberi URL HTTPS publik dan mengurus sertifikat TLS secara otomatis (Tailscale, n.d.). Docker Space atau PaaS sesuai Pertemuan 6 tetap menjadi alternatif karena menjalankan Dockerfile yang sama."),
("p", "Testing dan monitoring. pytest dipakai untuk API dan aturan, widget test Flutter untuk antarmuka, dan request HTTP langsung ke container untuk uji integrasi dan latency. Monitoring memakai latency_ms dan model_version di setiap response serta log container yang tidak memuat isi pesan."),
("p", "Pengamanan API. Rate limiting dan batas ukuran body ditulis sebagai dua middleware ASGI kecil, sehingga API terlindungi walaupun dijalankan tanpa reverse proxy dan tidak ada dependency baru. Server dijalankan dengan Uvicorn memakai 2 worker, batas 64 koneksi, dan keep-alive 5 detik (Uvicorn, n.d.)."),
]

S["2.4 Perubahan dari Proposal"] = [
("p", "Proposal sudah direvisi mengikuti implementasi sebelum laporan ini disusun, sehingga kebutuhan, arsitektur, dan teknologi pada laporan sama dengan proposal. Perubahan yang terjadi sejak Checkpoint 1 adalah sebagai berikut:"),
("b", "Model: diagram Checkpoint 1 menyebut Naive Bayes. Setelah dibandingkan, Logistic Regression dipilih karena F1 validasi silang lebih tinggi (0,919 dibanding 0,838)."),
("b", "Kriteria kualitas model: Checkpoint 1 hanya mensyaratkan akurasi ≥ 85%. Karena hanya 13,8% pesan berlabel phishing, model yang selalu menjawab aman sudah mencapai akurasi 86,1%. Kriteria diubah menjadi akurasi ≥ 85% dan F1 phishing ≥ 0,85."),
("b", "Penomoran NFR mengikuti template proposal: privasi menjadi NFR-03, kualitas model menjadi NFR-05, serta reliability (NFR-02) dan usability (NFR-04) ditambahkan."),
("b", "Fitur tambahan: lapisan aturan dan alasan (FR-04), popup dari menu seleksi teks (FR-05), dan menu Bagikan (FR-06). FR-06 dibuat setelah uji di HP menunjukkan teks SMS dan WhatsApp tidak dapat diseleksi."),
("b", "Keamanan: rate limiting, batas ukuran body, dan CORS terbatas ditambahkan sebelum API dibuka ke jaringan publik."),
("b", "Judi online: detektor judol dan aturan online_gambling ditambahkan setelah pesan klaim THR dari situs judol lolos saat aplikasi dicoba di live app. Promosi judol diberi label phishing."),
("b", "Checkpoint 1 menyebut penyorotan kata atau frasa mencurigakan sebagai versi lanjutan. Fitur ini belum dibuat; penjelasan baru berupa alasan dari lapisan aturan."),
("p", "Dua rencana pada proposal belum terlaksana: deployment cloud dengan HTTPS (Pertemuan 6) dan uji beban concurrent (Pertemuan 13). Keduanya dibahas sebagai backlog di BAB VI dan VII."),
]

S["3.1 Arsitektur Akhir Sistem"] = [
("img", "/home/zam/projects/MyProject/PhishGuard/mockups/arsitektur_v2.png", 15.0),
("cap", "Gambar 3.1 Arsitektur akhir sistem PhishGuard"),
("p", "Klien Flutter (APK Android atau web) mengirim teks ke REST API FastAPI dalam format JSON. Sebelum validasi, middleware memeriksa rate limit per IP dan ukuran body. API lalu memvalidasi input, memanggil layanan inference yang menjalankan model dan lapisan aturan, dan mengembalikan hasil. Penyimpanan hanya ada di dua tempat: berkas model phishguard.joblib di dalam image API dan riwayat di perangkat pengguna (shared_preferences). Log server hanya mencatat panjang teks, label, confidence, aturan, dan latency."),
("p", "API dan web berjalan sebagai dua container Docker (api di port 8000 dengan HEALTHCHECK, web nginx di port 8080 yang juga meneruskan /v1/ dan /health ke api). Pelatihan model berjalan terpisah (offline). Untuk akses publik, container sidecar ts-web (Tailscale) menerima HTTPS dari Funnel dan meneruskannya ke container web. Sistem tidak memakai layanan eksternal saat inference; dependency eksternal hanya pustaka Python dan Flutter yang versinya dikunci."),
]

S["3.2 System Flow dan Inference Flow"] = [
("b", "Input: pengguna menempel teks di layar utama, memilih teks lalu \"Scan dengan PhishGuard\", atau membagikan pesan lewat menu Bagikan."),
("b", "Validasi klien: teks kosong ditolak dengan pesan; kolom input membatasi 2.000 karakter, dan popup scan memotong teks yang lebih panjang dengan keterangan."),
("b", "Loading: tombol Analisis dinonaktifkan dan menampilkan indikator loading selama menunggu response."),
("b", "Request: klien mengirim POST /v1/predict ke alamat server yang tersimpan (default 10.0.2.2:8000 untuk emulator, localhost:8000 untuk web; dapat diubah di menu pengaturan)."),
("b", "Pengamanan: request di atas batas per menit pada satu worker dijawab 429 (bawaan 60, di docker-compose.yml 300; dihitung per alamat pengunjung, juga di belakang Funnel), dan body di atas 32 KB dijawab 413 sebelum JSON dibaca."),
("b", "Validasi server: Pydantic memeriksa field text; bila gagal, API menjawab 422 tanpa menjalankan model."),
("b", "Inference: TF-IDF kata dan karakter, lalu Logistic Regression menghitung peluang phishing. Lapisan aturan memeriksa teks. Label phishing diberikan bila peluang ≥ 0,5 atau ada aturan yang terpicu. Confidence adalah nilai terbesar antara peluang model dan skor aturan (0,85 sampai 0,95) untuk hasil phishing, atau peluang aman untuk hasil aman."),
("b", "Sukses: API menjawab 200; klien menampilkan kartu hasil, bar confidence, alasan, saran tindakan, dan menyimpan ringkasan ke riwayat."),
("b", "Gagal dan timeout: bila koneksi gagal atau melewati 10 detik, klien menampilkan \"Tidak bisa terhubung ke server\" beserta alamatnya. Status 422, 429, dan 413 masing-masing ditampilkan sebagai pesan input tidak valid, permintaan terlalu banyak, dan pesan terlalu besar."),
("b", "Retry: klien tidak mengulang request secara otomatis. Pengguna dapat menekan Analisis lagi; teks tetap ada di kolom input. Untuk 429, API mengirim header Retry-After."),
]

S["3.3 Kontrak API"] = [
("p", "API tidak memakai autentikasi karena tidak ada data pengguna yang disimpan; pembatasan akses dilakukan dengan rate limiting dan CORS. Dokumentasi OpenAPI interaktif tersedia di /docs saat server berjalan."),
("p", "Request POST /v1/predict (Content-Type: application/json):"),
("code", '{\n  "text": "Ini foto paket kakak ya, tolong dicek dulu: LIHAT_FOTO_PAKET.apk"\n}'),
("p", "Response 200:"),
("code", '{\n  "label": "phishing",\n  "confidence": 0.95,\n  "model_version": "tfidf_logreg-20261112",\n  "latency_ms": 4.3,\n  "reasons": [\n    "Meminta membuka/menginstal file .apk (modus APK undangan/paket/tilang)"\n  ]\n}'),
("p", "Response 422 (teks hanya spasi), mengikuti format validasi FastAPI:"),
("code", '{\n  "detail": [ {\n    "type": "value_error",\n    "loc": ["body", "text"],\n    "msg": "Value error, Teks pesan tidak boleh kosong"\n  } ]\n}'),
("p", "Response 429 (header Retry-After berisi detik sampai jendela berikutnya) dan 413:"),
("code", '{"detail": "Terlalu banyak permintaan, coba lagi sebentar"}\n{"detail": "Body request maksimal 32768 byte"}'),
]

S["3.4 Struktur Repository dan Dependency"] = [
("code", "phishguard/\n├── api/\n│   ├── app/main.py        endpoint FastAPI\n│   ├── app/rules.py       lapisan aturan\n│   ├── app/security.py    rate limit, batas body\n│   ├── tests/             pytest\n│   ├── Dockerfile\n│   └── requirements.txt\n├── model/                 phishguard.joblib, metrics.json\n├── src/data/prepare_dataset.py\n├── src/model/train.py\n├── data/                  raw, processed, challenge, README\n├── mobile/                aplikasi Flutter (lib, test, android)\n├── docs/                  checkpoint, proposal, laporan\n├── plans/                 rencana dan catatan pengujian\n├── mockups/               diagram dan screenshot\n├── docker-compose.yml\n├── requirements-dev.txt\n└── README.md"),
("p", "Pemisahan komponen: pelatihan (src/) tidak ikut ke image API; image API hanya berisi api/app dan model/phishguard.joblib; aplikasi Flutter hanya berkomunikasi lewat HTTP."),
("p", "Versi runtime dan dependency utama: Python 3.14, FastAPI 0.162.4, Uvicorn 0.54.0, Pydantic 2.14.3, scikit-learn 1.9.1, joblib 1.6.0, numpy 2.5.4, scipy 1.18.1 (dikunci di api/requirements.txt), Flutter 3.47.9, Docker 29.1.3. Versi scikit-learn dan joblib harus sama dengan saat pelatihan karena berkas Pickle bergantung pada versi pustaka."),
("p", "Konfigurasi lewat environment: MODEL_PATH, CORS_ORIGINS, RATE_LIMIT_PER_MIN (bawaan 60, diisi 300 di docker-compose.yml), MAX_BODY_BYTES (default 32768), dan FORWARDED_ALLOW_IPS yang berisi alamat tetap nginx dan sidecar (172.28.0.10 dan 172.28.0.11) sehingga Uvicorn membaca alamat pengunjung dari X-Forwarded-For hanya dari kedua proxy tersebut. Ringkasan endpoint:"),
]

S["4.1 Implementasi Model Inference dan Serialization"] = [
("p", "Skrip src/model/train.py membangun pipeline scikit-learn: FeatureUnion dua TfidfVectorizer (kata 1 sampai 2 gram dan char_wb 3 sampai 5 gram, min_df 2, sublinear_tf) lalu LogisticRegression (C=10, class_weight balanced, max_iter 2000). Praproses ada di dalam pipeline, sehingga teks mentah yang sama dipakai saat training dan inference."),
("p", "Model disimpan dengan joblib sebagai dictionary {pipeline, version, name, judol} di model/phishguard.joblib (5,6 MB), dengan judol berisi pipeline detektor judol dan ambangnya. API memuat berkas sekali saat start. Versi model berbentuk nama dan tanggal pelatihan (tfidf_logreg-20261112) dan dikirim di setiap response serta di /health. Metrik setiap pelatihan disimpan di model/metrics.json bersama hasil pemeriksaan NFR-05."),
("p", "Waktu prediksi rata-rata di dalam proses 0,167 ms per pesan untuk model utama dan 0,178 ms untuk detektor judol (diukur per batch). Contoh hasil inference lewat API: pesan \"Paket anda tertahan, unduh resi.apk untuk cek\" menghasilkan label phishing dengan confidence 0,95 dan alasan file .apk; pesan kurir J&T dari data kurasi menghasilkan phishing dengan confidence 0,957."),
]

S["4.2 Implementasi Backend/API"] = [
("p", "Service terdiri dari tiga modul. app/main.py memuat model, mendefinisikan skema Pydantic, endpoint, dan logging. app/rules.py berisi lima aturan regex (apk_attachment, share_code_request, paid_task_job, lookalike_domain, online_gambling) beserta daftar domain resmi. app/security.py berisi middleware rate limiting dan batas ukuran body."),
("p", "Validasi memakai Pydantic: text wajib, maksimal 2.000 karakter, dan validator yang menolak teks kosong atau hanya spasi. Kesalahan validasi ditangani exception handler bawaan FastAPI menjadi 422. Middleware menjawab 413 dan 429 sebelum request mencapai endpoint. Kesalahan lain menjadi 500 dari server."),
("p", "Logging: setiap prediksi mencatat satu baris berisi panjang teks, label, confidence, aturan yang terpicu, hasil detektor judol, dan latency. Isi pesan tidak pernah dicatat; hal ini diuji otomatis dengan mengirim teks unik lalu memeriksa log. Request ID belum diterapkan."),
("p", "Health check: GET /health mengembalikan status dan versi model. Image Docker memanggil endpoint ini setiap 30 detik."),
("p", "Keamanan: rate limiting per IP pada setiap worker (bawaan 60 request per menit, 300 pada docker-compose.yml), batas body 32 KB yang juga berlaku untuk body chunked, CORS hanya untuk origin web aplikasi, proses berjalan sebagai pengguna non-root di container, dan API hanya memuat berkas model buatan skrip pelatihan sendiri."),
]

S["4.3 Implementasi Frontend"] = [
("p", "Aplikasi Flutter terdiri dari main.dart (layar utama), api.dart (klien HTTP dan penanganan status), history.dart (riwayat dengan shared_preferences), widgets.dart (kartu hasil), dan scan.dart (popup). Di Android, ScanTextActivity menerima intent ACTION_PROCESS_TEXT dan ACTION_SEND, menjalankan entrypoint Dart scanMain di jendela transparan, dan mengirim teks lewat MethodChannel."),
("p", "State UI: idle (kolom input dan riwayat), loading (tombol nonaktif dengan indikator), hasil, dan error. Kartu hasil menampilkan label dengan ikon dan teks PHISHING atau AMAN sehingga hasil tetap terbaca tanpa membedakan warna, teks \"Keyakinan: x%\" dengan bar, daftar \"Tanda bahaya terdeteksi\" dari field reasons, saran tindakan, serta versi model dan latency."),
("p", "Penanganan error: koneksi gagal atau timeout 10 detik, status 422, 429, 413, dan status lain masing-masing memiliki pesan sendiri. Alamat server dapat diubah lewat ikon pengaturan dan disimpan di perangkat."),
]

S["4.4 Containerization dan Konfigurasi Environment"] = [
("p", "api/Dockerfile memakai python:3.14-slim, memasang dependency dari requirements.txt, menyalin api/app dan model/phishguard.joblib saja (diatur .dockerignore), membuat pengguna sistem non-root, memasang HEALTHCHECK ke /health, dan menjalankan Uvicorn dengan 2 worker, limit-concurrency 64, dan timeout-keep-alive 5 detik. mobile/Dockerfile.web menyajikan hasil flutter build web dengan nginx:1.27-alpine."),
("p", "mobile/nginx.conf menyajikan web dan meneruskan /v1/ serta /health ke container api dengan batas body 32 KB dan timeout 10 detik. docker-compose.yml menjalankan container api (port 8000) dan web (port 8080) serta mengisi CORS_ORIGINS, RATE_LIMIT_PER_MIN, dan MAX_BODY_BYTES. Layanan tidak memakai secret; bila nanti ada, secret disimpan di environment platform dan tidak di-commit."),
("p", "Cara menjalankan:"),
("code", "cd mobile && flutter build web --release && cd ..\ndocker compose up -d --build\ncurl http://localhost:8080/health"),
]

S["4.5 Bukti Implementasi"] = [
("img", "/home/zam/projects/MyProject/PhishGuard/mockups/ui_android_v2.png", 15.0),
("cap", "Gambar 4.1 Aplikasi PhishGuard di Android: (a) input, (b) hasil phishing dengan tanda bahaya, (c) hasil aman dan riwayat, (d) popup scan dari seleksi teks, (e) server tidak terjangkau, (f) popup dari menu Bagikan di atas percakapan SMS"),
("p", f"Implementasi yang dilaporkan sesuai dengan commit {COMMIT} di {REPO} (branch main). Tag release belum dibuat. Screenshot (a) sampai (e) diambil di emulator Android 36; (f) diambil di emulator dengan intent ACTION_SEND yang sama dengan menu Bagikan."),
]

S["5.1 Strategi dan Lingkungan Pengujian"] = [
("p", "Pengujian dilakukan berlapis: data (reproduksibilitas split), model (metrik pada data uji dan challenge set), unit test API dan aturan, integration test pada container, widget test Flutter, end-to-end di browser dan Android, latency, dan keamanan."),
("p", "Lingkungan: laptop AMD Ryzen 5 7520U (8 thread), RAM 7 GB, Ubuntu 26.04.1 LTS, Python 3.14.4, Docker 29.1.3 dengan Docker Compose 2.40.3, Flutter 3.47.9, Chrome, emulator Android 36 (AVD phishguard_test), dan satu HP Android milik anggota kelompok. Jaringan: localhost, Wi-Fi lokal, dan internet lewat Tailscale Funnel (https://phishguard.taile0ea7c.ts.net)."),
("p", "Data uji: 1.413 pesan test.csv, 21 pesan challenge set, dan pesan contoh pada tes. Prosedur reproduksi:"),
("code", "python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt\n.venv/bin/python src/data/prepare_dataset.py\n.venv/bin/python src/model/train.py\ncd api && ../.venv/bin/python -m pytest -q\ncd ../mobile && flutter test"),
]

TESTS = [
    ("T-01", "POST /v1/predict teks valid ke container", "200, body sesuai skema", "200, 5 field sesuai skema", "Lulus", "test_api.py; uji live"),
    ("T-02", "Teks kosong, spasi, 2.001 karakter, field hilang", "422 dengan pesan validasi", "422; teks 2.000 karakter diterima 200", "Lulus", "test_api.py; uji live"),
    ("T-03", "Server API dimatikan (docker compose stop api)", "Pesan \"Tidak bisa terhubung\", tidak crash", "Pesan tampil di app dan popup", "Lulus", "Gambar 4.1 (e)"),
    ("T-04", "19 kasus aturan positif/negatif; seluruh 6.089 pesan aman", "Aturan hanya terpicu pada pola penipuan", "19/19; 0 false alarm", "Lulus", "test_rules.py"),
    ("T-05", "Kirim teks unik lalu periksa log", "Teks tidak muncul di log", "Hanya panjang/label/latency", "Lulus", "test_api.py; log container"),
    ("T-06", "Rate limit: request beruntun dari satu IP", "429 + Retry-After setelah batas", "Lulus; lihat 5.4 untuk angka", "Lulus", "test_security.py; uji live"),
    ("T-07", "Body 40 KB biasa dan chunked", "413 sebelum JSON dibaca", "413", "Lulus", "test_security.py; uji live"),
    ("T-08", "Preflight CORS dari origin lain dan dari :8080", "Origin lain ditolak", "Lain 400 tanpa ACAO; :8080 200", "Lulus", "test_security.py; curl"),
    ("T-09", "Widget dan unit test Flutter (kosong, phishing, aman, alasan, server mati, 429, popup, alamat API bawaan)", "Tampilan dan alamat sesuai state", "14/14 lulus", "Lulus", "mobile/test"),
    ("T-10", "Prepare dataset dijalankan ulang", "train/test identik", "md5 sama", "Lulus", "full-testing.md"),
    ("T-11", "Web di :8080 lewat Chrome: scan pesan, lalu cek tujuan request", "Request ke /v1/predict di origin yang sama, hasil tampil", "Request ke localhost:8080/v1/predict; PHISHING 95,0%", "Lulus", "Playwright + Chrome"),
    ("T-12", "URL publik https://phishguard.taile0ea7c.ts.net dari luar tailnet (DNS publik): halaman, /health, scan, 40 KB, port 8000", "200, prediksi benar, 413, port 8000 tertutup", "200 (TLS valid); .apk PHISHING 0,95; teks rapat AMAN 0,963; 413; 8000 tidak terjangkau; Chrome: request ke origin publik", "Lulus", "curl, Playwright + Chrome, fetch eksternal"),
    ("T-13", "Pesan judol dari user (klaim THR, akaligabandar.mom), promo judol tanpa tautan, kampanye anti-judol, kode diskon THR resmi", "Judol phishing dengan alasan; anti-judol dan promo resmi aman", "Sesuai harapan di pytest dan di URL publik; pesan user PHISHING 90% dengan alasan situs judol", "Lulus", "test_rules.py; curl; Playwright"),
    ("T-14", "Seluruh 7.067 SMS lama lewat logika API sebelum dan sesudah penambahan judol", "Tidak ada label yang berubah", "Aman ditandai: 34 sebelum dan sesudah; phishing terdeteksi: 962 sebelum dan sesudah", "Lulus", "skrip perbandingan"),
]

S["5.2 Hasil Unit dan Integration Testing"] = [
("p", "Seluruh tes dijalankan ulang pada 12 November 2026: 46 tes pytest lulus dan 14 tes Flutter (widget dan unit) lulus. Ringkasan per skenario:"),
]

S["5.3 Hasil End-to-End User Test"] = [
("p", "Uji end-to-end dilakukan oleh pengembang di Chrome (aplikasi web), di emulator Android 36 (APK release), dan oleh ketua kelompok di HP Android asli. Uji dengan pengguna di luar kelompok belum dilakukan."),
("b", "Web: input kosong menampilkan pesan validasi; pesan dengan file .apk menghasilkan PHISHING 95% dengan alasan dan masuk riwayat."),
("b", "Android, aplikasi utama: pesan DANA dengan domain palsu menghasilkan PHISHING 85% dengan alasan domain; pesan rapat kelompok menghasilkan AMAN 98,6%; riwayat tersimpan."),
("b", "Android, popup seleksi teks dari cold start (aplikasi dihentikan paksa terlebih dahulu): pesan .apk PHISHING 95% dalam sekitar 1,5 detik sejak dibuka; permintaan OTP PHISHING 90%; template OTP resmi WhatsApp AMAN 83,6%."),
("b", "HP Android asli: SMS yang dibagikan lewat menu Bagikan memunculkan popup hasil."),
("p", "Masalah UI/UX yang ditemukan dan perbaikannya:"),
("b", "Di aplikasi SMS dan WhatsApp, teks pesan tidak dapat diseleksi, sehingga menu \"Scan dengan PhishGuard\" tidak muncul. Perbaikan: PhishGuard didaftarkan sebagai tujuan Bagikan (FR-06). Uji ulang di HP asli berhasil."),
("b", "Setelah rate limiting ditambahkan, aplikasi menampilkan \"Server error (429)\". Perbaikan: pesan \"Terlalu banyak permintaan. Tunggu sebentar lalu coba lagi.\" dan widget test baru."),
("b", "HP asli tidak dapat memakai alamat bawaan 10.0.2.2 (hanya berlaku di emulator). Pengguna perlu mengisi alamat IP laptop lewat menu pengaturan. Masalah ini baru akan hilang setelah API memiliki URL publik."),
]

S["5.4 Hasil Latency dan Stress Test"] = [
("p", "Latency diukur sebagai waktu respons HTTP dari sisi klien ke container API di localhost, dengan request berurutan (concurrency 1):"),
("b", "Sebelum pengamanan API: 300 request, p50 3,9 ms, p95 4,5 ms, maksimum 6,5 ms, tanpa request gagal."),
("b", "Setelah pengamanan API (12 November 2026, 10.54): 55 request, semuanya 200, p50 3,9 ms, p95 5,3 ms, maksimum 42,4 ms. Jumlah request dibatasi di bawah rate limit agar tidak tercampur jawaban 429."),
("b", "Setelah detektor judol ditambahkan (12 November 2026, 14.35), sehingga setiap request menjalankan dua model: 55 request, semuanya 200, p50 5,3 ms, p95 8,3 ms, maksimum 13,5 ms."),
("p", "Di dalam proses, prediksi rata-rata 0,167 ms per pesan untuk model utama dan 0,178 ms untuk detektor judol, sehingga hampir seluruh waktu respons berasal dari HTTP dan framework. Target NFR-01 (p95 < 3 detik) terpenuhi. Pengukuran ini belum mencakup jaringan internet."),
("p", "Pengujian rate limit memperlihatkan perilaku yang perlu dicatat. Dengan 150 request dari curl yang membuka koneksi baru setiap request, 120 request diterima dan 30 dijawab 429, karena request tersebar ke 2 worker yang masing-masing menghitung 60 per menit. Dengan satu klien yang memakai koneksi keep-alive, 60 request diterima dan 40 dari 100 dijawab 429, karena semua request masuk ke worker yang sama. Batas efektif per IP dengan demikian berada di antara 60 dan 120 request per menit. Setelah batas dinaikkan menjadi 300 dan request dilewatkan nginx, 700 request beruntun lewat port 8080 menghasilkan 597 jawaban 200 dan 103 jawaban 429 dengan Retry-After, sesuai batas 2 worker × 300."),
("p", "Stress test bertingkat dengan Locust (minimal empat tingkat beban dengan p50, p95, RPS, error rate, dan resource usage) belum dilakukan. Uji ini dijadwalkan pada Pertemuan 13. Saat uji, RATE_LIMIT_PER_MIN perlu dinaikkan sementara agar hasilnya tidak didominasi 429. Throughput, p99, error rate di bawah beban, bottleneck, dan tindakan optimasi akan dilaporkan setelah uji tersebut: [hasil stress test]."),
]

S["5.5 Evaluasi Model dan XAI"] = [
("p", "Pada 1.413 pesan uji, model mencapai akurasi 0,978, precision 0,923, recall 0,918, dan F1 phishing 0,921. Dari 196 pesan phishing, 16 lolos; dari 1.217 pesan aman, 15 salah ditandai. Per bahasa, F1 phishing 0,901 untuk Inggris (1.160 pesan) dan 0,944 untuk Indonesia (253 pesan). Model yang selalu menjawab aman hanya mencapai akurasi 0,861 dan F1 0. Target NFR-05 terpenuhi."),
("p", "Detektor judol diuji pada 772 posting judol yang tidak dipakai pelatihan: precision 0,976, recall 0,933, dan F1 0,954 (7 posting bukan judol salah ditandai, 20 promosi judol lolos). Pada seluruh 6.089 SMS aman di data latih dan uji, detektor tidak pernah menyala. Bila model utama dan detektor dipakai bersama pada 772 posting tersebut, precision turun menjadi 0,648 karena model utama menandai 152 posting media sosial biasa yang bertautan sebagai phishing. Model utama dilatih untuk SMS, sehingga hasil pada posting media sosial perlu dibaca dengan hati-hati."),
("p", "Pada challenge set modus baru, hasilnya lebih rendah. Challenge v1 (9 pesan) benar semua, sebagian karena data kurasi berisi modus yang sama. Challenge v2 (12 pesan, ditulis setelah pelatihan ulang) benar 8 dengan model saja: kurir APK, foto paket APK, dan lowongan paruh waktu lolos, serta notifikasi debit BCA asli ditandai phishing. Dengan lapisan aturan hasilnya 11 dari 12, tetapi angka ini optimis karena aturan dirancang setelah melihat pesan yang lolos. Lewat API, gabungan v1 dan v2 benar 20 dari 21."),
("p", "Contoh kesalahan pada data uji menunjukkan batas label yang kabur antara spam dan smishing pada dataset Mendeley. Pesan \"U are subscribed to the best Mobile Content Service in the UK for £3 per ten days...\" berlabel smishing tetapi diberi peluang phishing 0,027. Sebaliknya, \"We tried to contact you re your reply to our offer of a Video Phone...\" berlabel spam (aman) tetapi diberi peluang phishing 0,999. Sebagian kesalahan model berasal dari label sumber yang tidak konsisten."),
("p", "Explainability. Penjelasan kepada pengguna berupa alasan dari lapisan aturan. Untuk analisis pengembang, koefisien Logistic Regression dibaca langsung. Fitur dengan bobot phishing terbesar antara lain n-gram karakter \" 08\" (awal nomor telepon, 5,32), \"claim\" (3,74), \"anda\" (3,44), \"hub\" (3,38), \"http\" (3,05), \"hadiah\" (2,72), dan \"klik\" (2,31). Bobot terbesar ke arah aman antara lain \"and\" (-2,88), \"aku\" (-1,85), \"ok\" (-1,71), dan \"nama1\" (-1,68)."),
("p", "Bobot ini memperlihatkan bias data. Kata sapaan formal \"anda\" mendorong ke phishing dan kata informal \"aku\" ke aman, sehingga pesan resmi yang sopan berisiko ditandai phishing. Pada notifikasi debit BCA asli di challenge v2 (peluang phishing 0,803), penyumbang terbesar adalah \"anda\" (+0,51), \"000\" dari nominal uang (+0,48), dan \"bca\" (+0,47). Token \"nama1\" berasal dari anonimisasi dataset Rahmi dan tidak akan muncul di pesan nyata."),
("p", "Batas penggunaan: hasil hanya bantuan awal, dan keputusan tetap pada pengguna. Model belum diuji pada email panjang, belum mengenali modus yang tidak ada di data latih kecuali yang ditangkap aturan, dan confidence menyatakan keyakinan model sehingga tidak menjamin sebuah pesan aman."),
]

S["5.6 Analisis Kegagalan dan Perbaikan"] = [
("b", "Model gagal mengenali modus 2022 ke atas. Challenge v1 awalnya hanya mendeteksi 1 dari 5 penipuan karena data Indonesia berasal dari tahun 2016. Solusi: 69 teks penipuan terbaru dikurasi dari berita dan data bopbi ditambahkan, lalu model dilatih ulang. Uji ulang: challenge v1 9/9, F1 uji naik dari 0,914 ke 0,921."),
("b", "Kata \".apk\" tidak dikenal model. Solusi: lapisan aturan. Uji ulang: challenge v2 naik dari 8/12 ke 11/12, dan akurasi data uji tetap 0,978."),
("b", "Aturan awal memicu false alarm pada pesan seperti \"pin lokasi\" dan lowongan yang hanya menyebut gaji. Solusi: pengecualian dan syarat tarif per tugas. Uji ulang: 0 false alarm pada 6.089 pesan aman."),
("b", "Pesan klaim THR dari situs judol (\"Ke cici01 peener1ma THR 275.000! akaligabandar.mom ...\") lolos sebagai aman 0,75 saat dicoba di live app. Pemeriksaan menunjukkan penyebab utamanya adalah tidak adanya data judi online di data latih, karena versi pesan dengan ejaan normal juga dinilai aman. TLD .mom juga belum dikenali aturan. Solusi: dataset judol berlisensi CC BY 4.0, detektor judol terpisah, aturan online_gambling (domain berkosakata judi atau minimal dua istilah promosi judol dengan tautan, dicocokkan setelah normalisasi angka ke huruf), dan TLD baru. Uji ulang: pesan tersebut PHISHING 90% dengan alasan situs judol, 0 false alarm aturan dan detektor pada 6.089 SMS aman dan 2.362 posting bukan judol, dan tidak ada label SMS lama yang berubah."),
("b", "Teks SMS dan WhatsApp tidak dapat diseleksi sehingga popup tidak dapat dipanggil. Solusi: menu Bagikan (FR-06). Uji ulang di HP asli berhasil."),
("b", "API terbuka tanpa pembatasan. Solusi: rate limiting, batas body, CORS terbatas, dan batas koneksi. Uji ulang: 36 pytest dan uji langsung lulus."),
("b", "Emulator dimatikan sistem karena RAM laptop (7 GB) habis saat build APK berjalan bersamaan. Emulator juga berhenti sekali saat Google Messages dipakai, dengan dugaan penyebab yang sama. Solusi: build APK sebelum emulator dinyalakan dan memori emulator dibatasi. Masalah ini terjadi di lingkungan pengembangan dan tidak memengaruhi aplikasi."),
("p", "Belum terselesaikan: false alarm pada notifikasi transaksi BCA asli (lapisan aturan hanya menambah sinyal phishing dan tidak dapat mengoreksi model), modus yang menghindari aturan (misalnya \"a p k\" atau tautan pendek), dan kebutuhan challenge v3 yang ditulis orang di luar pengembang agar evaluasi lebih adil."),
]

S["6.1 Deployment dan Release"] = [
("p", "Aplikasi berjalan dengan Docker Compose di laptop pengembang: API di http://localhost:8000 dan web di http://localhost:8080. HP di Wi-Fi yang sama dapat memakai alamat IP laptop. Akses publik tersedia di https://phishguard.taile0ea7c.ts.net sejak 12 November 2026."),
("p", "Akses publik memakai Tailscale Funnel yang dijalankan sebagai container sidecar ts-web di laptop yang sama (Tailscale, n.d.). Container ini menjadi node tailnet sendiri bernama phishguard, sehingga Tailscale di host tidak perlu diubah, dan Funnel menyala atau mati bersama container (docker compose --profile public up -d). Nginx pada container web sudah meneruskan /v1/ dan /health ke container api (mobile/nginx.conf), sehingga web dan API berada di satu origin dan hanya port web yang perlu dibuka. Web memanggil API dengan alamat origin halaman, kecuali saat dijalankan dengan flutter run, dan APK diarahkan ke URL HTTPS lewat pengaturan alamat server. Funnel hanya dinyalakan saat demo dan penilaian, karena laptop harus tetap menyala selama URL dipakai. Sertifikat HTTPS untuk phishguard.taile0ea7c.ts.net dibuat otomatis oleh sidecar. Uji pada 12 November 2026 lewat DNS publik: satu request membutuhkan sekitar 0,8 detik, sebagian besar untuk koneksi dan TLS melalui relay Funnel, dibanding 2 sampai 5 ms di localhost. Dengan 32 koneksi paralel, 800 request selesai dalam 5 menit 23 detik (sekitar 2,5 request per detik), 766 berhasil dan 34 gagal terhubung. Jalur Funnel menjadi bottleneck sebelum batas rate limit tercapai, sehingga uji beban P13 sebaiknya dijalankan ke port lokal dan hasil Funnel dilaporkan terpisah. Docker Space atau PaaS (Pertemuan 6) menjadi alternatif bila cara ini tidak dapat dipakai. URL: https://phishguard.taile0ea7c.ts.net."),
("p", f"Build dan release: image dibangun dengan docker compose build, APK dengan flutter build apk --release, dan web dengan flutter build web --release. Versi model tercatat di model_version, API 1.0.0, dan aplikasi 1.0.0+1. Kode berada di commit {COMMIT}; tag release belum dibuat. Secret belum ada. Rollback dilakukan dengan kembali ke commit dan image stabil sebelumnya bila versi baru gagal health check atau metriknya turun."),
]

S["6.2 Monitoring dan Operasional"] = [
("p", "Health check: HEALTHCHECK container memanggil /health setiap 30 detik dengan batas waktu 3 detik, dan status container terlihat di docker ps (healthy/unhealthy)."),
("p", "Log dan metrik: setiap prediksi mencatat panjang teks, label, confidence, aturan, dan latency tanpa isi pesan. Response memuat latency_ms dan model_version. Error rate dihitung dari proporsi status selain 200 pada log. Request ID, pemantauan resource usage, dan alert otomatis belum diterapkan."),
("p", "Prosedur pemulihan: bila API tidak menjawab, periksa docker compose ps dan docker compose logs api, jalankan docker compose restart api, lalu uji ulang /health. Bila berkas model gagal dimuat, pastikan versi scikit-learn sesuai requirements.txt atau latih ulang model."),
]

S["6.3 Dokumentasi Penggunaan"] = [
("p", f"Instalasi dan menjalankan lokal dijelaskan di README repository ({REPO}): siapkan venv Python dan pasang requirements-dev.txt, bangun web Flutter, lalu jalankan docker compose up -d --build. Untuk Android, pasang APK hasil flutter build apk --release."),
("p", "Penggunaan aplikasi: tempel pesan di kolom input lalu tekan Analisis; atau di Android, seleksi teks lalu pilih \"Scan dengan PhishGuard\"; atau di aplikasi SMS/WhatsApp tekan lama pesan, pilih Bagikan, lalu \"Scan dengan PhishGuard\". Di HP asli, isi alamat server lewat ikon pengaturan dengan IP laptop, misalnya http://192.168.x.x:8000."),
("p", "Dokumentasi API: /docs (OpenAPI) dan subbab 3.3."),
("p", "Troubleshooting:"),
("b", "\"Tidak bisa terhubung ke server\": pastikan container api berjalan, HP dan laptop di jaringan yang sama, dan alamat server benar."),
("b", "\"Terlalu banyak permintaan\": tunggu sampai satu menit."),
("b", "Menu \"Scan dengan PhishGuard\" tidak muncul saat menekan lama pesan SMS: gunakan menu Bagikan."),
("p", "Batas penggunaan: hanya teks hingga 2.000 karakter, dan hasil merupakan bantuan awal."),
]

S["6.4 Keamanan, Privasi, dan Etika"] = [
("p", "Kontrol yang diterapkan: rate limiting per IP, batas body 32 KB, CORS terbatas, batas 64 koneksi dan keep-alive 5 detik, container non-root, validasi input, dan pemuatan berkas model buatan sendiri saja. Akses publik memakai HTTPS dengan sertifikat yang dibuat oleh sidecar Tailscale, dan port API 8000 tidak dibuka ke internet."),
("p", "Rate limit di belakang Tailscale Funnel: uji awal pada 12 November 2026 menunjukkan header X-Forwarded-For berisi 100.123.90.35, sehingga kelompok sempat menyimpulkan Funnel tidak meneruskan alamat pengunjung. Setelah deployment, log nginx menunjukkan kesimpulan itu keliru: 100.123.90.35 adalah alamat tailnet laptop pengirim, karena request uji tersebut lewat tailnet. Request dari internet membawa alamat publik asli pengunjung, dan header X-Forwarded-For palsu dari klien dibuang oleh Tailscale. Karena itu API dikonfigurasi memercayai X-Forwarded-For hanya dari nginx dan sidecar. Uji ulang dengan batas sementara 5 request per menit: alamat publik laptop menerima 429 setelah 10 request (2 worker), sedangkan alamat lain tetap dijawab 200, dan header palsu lewat localhost, IP LAN, maupun URL publik tidak mengubah alamat yang dibaca API. Rate limit dengan demikian berlaku per pengunjung, dengan batas 300 request per menit per worker."),
("p", "Data yang disimpan dan tidak disimpan: isi pesan tidak disimpan di server dan tidak dicatat di log. Riwayat (cuplikan 80 karakter, label, confidence, waktu) hanya disimpan di perangkat pengguna dan dapat dihapus. Aplikasi Android hanya meminta izin INTERNET. Pesan dikirim ke API hanya ketika pengguna memilih menganalisisnya, sehingga tindakan tersebut menjadi bentuk persetujuan pengguna."),
("p", "Bias: data latih didominasi bahasa Inggris dan modus lama, dan model condong menandai bahasa formal sebagai phishing (subbab 5.5). Notifikasi resmi dapat ditandai phishing."),
("p", "Label judi online: promosi judi online diberi label phishing walaupun bentuknya iklan, karena judol ilegal di Indonesia dan situsnya menjadi pintu penipuan. Kampanye anti-judol dan berita tentang judol tetap diberi label aman dan dipakai sebagai contoh pembanding saat pelatihan, supaya kata \"judi\" saja tidak membuat pesan ditandai."),
("p", "Penyalahgunaan: karena response memuat confidence dan alasan, penyerang dapat mengubah pesan penipuan sedikit demi sedikit dan mengirimnya berulang sampai labelnya berubah menjadi aman. Rate limiting memperlambat percobaan ini tetapi tidak mencegahnya. Fitur alasan tetap dipertahankan karena membantu pengguna menilai hasil, sehingga risiko ini dicatat sebagai keterbatasan."),
("p", "Disclaimer: kartu hasil selalu menampilkan saran umum (jangan klik tautan, jangan bagikan OTP/PIN, jangan transfer uang), dan hasil PhishGuard tidak menjamin sebuah pesan aman."),
]

S["7.1 Kesimpulan"] = [
("b", "Model TF-IDF dengan Logistic Regression mencapai akurasi 97,8% dan F1 phishing 0,921 pada 1.413 pesan uji, sehingga pertanyaan evaluasi pertama terjawab dan NFR-05 terpenuhi."),
("b", "API menolak input tidak valid dengan 422, membatasi penyalahgunaan dengan 429 dan 413, dan menjawab dengan latency p95 8,3 ms di container lokal (dua model per request), jauh di bawah target 3 detik."),
("b", "Promosi judi online kini dikenali oleh detektor judol (F1 0,954 pada data uji judol) dan aturan online_gambling, tanpa mengubah satu pun label pada 7.067 SMS lama."),
("b", "Pengguna dapat memeriksa pesan dari aplikasi Flutter, dari menu seleksi teks, dan dari menu Bagikan; ketiganya sudah diuji, termasuk menu Bagikan di HP asli. Uji dengan pengguna di luar kelompok belum dilakukan."),
("b", "Kemampuan mengenali modus Indonesia terbaru masih terbatas: model saja benar 8 dari 12 pesan challenge v2. Lapisan aturan menaikkannya menjadi 11 dari 12, dengan catatan angka tersebut optimis. Penyebab utamanya adalah sedikitnya data penipuan Indonesia terbaru di data latih."),
]

S["7.2 Keterbatasan"] = [
("b", "Data: 82% data uji SMS berbahasa Inggris, modus Indonesia terbaru sedikit, dan sebagian label spam dan smishing tidak konsisten. Data judol berasal dari caption media sosial, bukan SMS, sehingga kinerja detektor judol pada SMS judol asli belum terukur."),
("b", "Model: bias ke bahasa formal, belum diuji pada email panjang, dan aturan dapat dihindari dengan mengubah penulisan."),
("b", "Infrastruktur: belum ada request ID, alert, maupun stress test bertingkat. Rate limiting dihitung per worker di memori. Akses publik bergantung pada laptop pengembang yang harus menyala, dan setiap request lewat Funnel membutuhkan sekitar 0,8 detik."),
("b", "Evaluasi: challenge set kecil (21 pesan) dan ditulis oleh pengembang; uji pengguna belum melibatkan orang di luar kelompok."),
("b", "Keamanan: risiko oracle dari confidence dan alasan."),
("b", "UI/UX: di HP asli pengguna harus mengisi alamat server secara manual."),
]

S["7.3 Rencana Pengembangan"] = [
("p", "Prioritas berdasarkan hasil evaluasi:"),
("b", "Mengumpulkan SMS dan WhatsApp judol asli untuk menguji detektor judol pada bentuk pesan yang sebenarnya dipakai pengguna."),
("b", "Stress test Locust minimal empat tingkat beban, analisis bottleneck, satu perbaikan, dan uji ulang (Pertemuan 13)."),
("b", "Mengumpulkan SMS/WhatsApp asli dari anggota kelompok, baik penipuan maupun notifikasi resmi, lalu melatih ulang model untuk mengurangi false alarm notifikasi bank."),
("b", "Challenge v3 yang ditulis orang di luar pengembang dan uji pengguna di luar kelompok."),
("b", "Request ID di log dan response, pemantauan resource usage, dan tag release."),
("b", "Penyorotan kata yang paling berpengaruh pada prediksi, memakai koefisien model."),
]

S["DAFTAR PUSTAKA"] = [
("ref", "Al Hakim, T. (2026, 9 Januari). OJK terima 411.055 laporan penipuan transaksi keuangan, kerugian capai Rp 9 triliun. Investortrust.id. https://investortrust.id/financial/90898/ojk-terima-411055-laporan-penipuan-transaksi-keuangan-kerugian-capai-rp-9-triliun"),
("ref", "Bank Central Asia. (2025, 26 Januari). Hati-hati penipuan smishing mengatasnamakan BCA. https://www.bca.co.id/id/informasi/awas-modus/2025/01/26/15/08/Hati-Hati-Penipuan-Smishing-Mangatasnamakan-BCA"),
("ref", "bopbi. (2021). Indonesia SMS spam dataset [Data set]. GitHub. https://github.com/bopbi/indonesia-sms-spam-dataset"),
("ref", "Docker. (n.d.). Docker documentation. Diakses 12 November 2026, dari https://docs.docker.com"),
("ref", "Ekaputra, D. R. (2026). Indonesian online gambling promotion multimodal dataset [Data set]. Hugging Face. https://huggingface.co/datasets/0xRafie/indonesian-gambling-multimodal-dataset"),
("ref", "FastAPI. (n.d.). FastAPI documentation. Diakses 12 November 2026, dari https://fastapi.tiangolo.com"),
("ref", "Flutter. (n.d.). Flutter documentation. Diakses 12 November 2026, dari https://docs.flutter.dev"),
("ref", "Google. (n.d.). Intent. Android Developers. Diakses 12 November 2026, dari https://developer.android.com/reference/android/content/Intent"),
("ref", "Mishra, S., & Soni, D. (2022). SMS phishing dataset for machine learning and pattern recognition (Version 1) [Data set]. Mendeley Data. https://doi.org/10.17632/f45bkkt8pr.1"),
("ref", "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830."),
("ref", "Rahmi, F., & Wibisono, Y. (2016). Aplikasi SMS spam filtering pada Android menggunakan naive Bayes [Naskah tidak dipublikasikan]. Dataset v1.0 (2018). https://yudiwbs.wordpress.com/2018/08/05/dataset-klasifikasi-bahasa-indonesia-sms-spam-klasifikasi-teks-dengan-scikit-learn/"),
("ref", "Tailscale. (n.d.). Tailscale Funnel. Diakses 12 November 2026, dari https://tailscale.com/kb/1223/funnel"),
("ref", "Tim Cek Fakta. (2022, 9 Desember). Awas, beredar pesan WA berisi file APK mengatasnamakan tagihan PLN. Kompas.com. https://www.kompas.com/cekfakta/read/2022/12/09/144037282/awas-beredar-pesan-wa-berisi-file-apk-mengatasnamakan-tagihan-pln"),
("ref", "Tim Cek Fakta. (2023, 4 Agustus). [HOAKS] Tawaran kerja paruh waktu terkait promosi di TikTok. Kompas.com. https://www.kompas.com/cekfakta/read/2023/08/04/140000382/-hoaks-tawaran-kerja-paruh-waktu-terkait-promosi-di-tiktok"),
("ref", "Uvicorn. (n.d.). Settings. Diakses 12 November 2026, dari https://uvicorn.dev/settings/"),
]

LAMPIRAN_ROWS = [
    ("A", "URL live app dan repository/tag release", f"Live app: belum tersedia. Repository: {REPO} (commit {COMMIT}; tag belum dibuat)"),
    ("B", "README, API documentation, dan panduan instalasi", "README.md di repository; /docs saat server berjalan; subbab 3.3 dan 6.3"),
    ("C", "Diagram arsitektur dan system flow resolusi penuh", "mockups/arsitektur_v2.png (sumber mockups/arsitektur_v2.html); subbab 3.2"),
    ("D", "Bukti test, log, latency, dan stress test", "plans/2026-11-12-full-testing.md, plans/2026-11-12-keamanan-api.md, model/metrics.json, api/tests/; stress test: [belum dilakukan]"),
    ("E", "Screenshot UI dan end-to-end user test", "mockups/screenshots/ dan Gambar 4.1"),
    ("F", "Log kontribusi anggota/commit", f"{REPO}/commits/main; [log kontribusi per anggota diisi kelompok]"),
]

# Checklist penyerahan akhir, sesuai kondisi sebenarnya.
CHECKLIST = [False, True, True, False, True, False]
