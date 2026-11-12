import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rules import check

client = TestClient(app)


@pytest.mark.parametrize("text,rule", [
    ("Ini foto paket kakak ya, tolong dicek dulu: LIHAT_FOTO_PAKET.apk", "apk_attachment"),
    ("Undangan Pernikahan Digital.APK silakan dibuka", "apk_attachment"),
    ("Mohon maaf saya salah kirim kode verifikasi ke nomor anda, tolong kirimkan kode 6 digit itu ke saya", "share_code_request"),
    ("Petugas kami akan menghubungi, mohon sebutkan kode OTP tersebut untuk verifikasi hadiah", "share_code_request"),
    ("Kerja paruh waktu, cukup like video dapat 50rb per tugas", "paid_task_job"),
    ("Part time job: follow akun toko, komisi Rp 100.000/hari", "paid_task_job"),
    ("Tarif transfer naik, isi form di bca-tarif.id", "lookalike_domain"),
    ("Akun DANA Anda diblokir, verifikasi di https://dana-verifikasi.id/login", "lookalike_domain"),
    ("Paket tertahan, update alamat di jnt-ekspres.xyz", "lookalike_domain"),
    # Real message reported by the user (2026-11-12): judol site with an obfuscated "claim THR" lure
    ("Ke cici01 peener1ma THR 275.000! akaligabandar.mom aambil skrg pkai k0dee : PUASA2026", "online_gambling"),
    ("Bonus deposit 100% slot gacor, daftar sekarang di akaligabandar.mom", "online_gambling"),
    ("SLOT GAC0R hari ini, RTP live maxwin, daftar: https://bit.ly/xyz123", "online_gambling"),
    ("Info jackpot terbaru cek di www.maxwinsk.com", "online_gambling"),
])
def test_rule_fires(text, rule):
    assert rule in [h.id for h in check(text)]


@pytest.mark.parametrize("text", [
    "Kode OTP Gojek kamu 482913. JANGAN berikan kode ini ke siapa pun, termasuk pihak Gojek.",
    "Kode verifikasi WhatsApp Anda: 482-913. Jangan bagikan kode ini.",
    "Jgn pernah kasih kode OTP ke orang lain ya, banyak penipuan sekarang",
    "Nanti kirim pin lokasi rumahmu ya biar aku ga nyasar",  # 'pin lokasi' is not a code request
    "Info lengkap kunjungi www.bca.co.id atau hubungi Halo BCA 1500888",
    "Cek status paket di https://jet.co.id/track",
    "Daftar ulang BPJS di https://bpjs-kesehatan.go.id ya",
    "Aku like banget sama kerjaan baru, gajinya 5 juta",  # salary mention, not a pay-per-task offer
    "Selamat pagi, rapat dimulai jam 9 di ruang 402",
    "Dari BRI.Klaim asuransi bisa lewat kantor cabang",  # missing space after full stop is not a domain
    # judol-related but legitimate: campaigns, news, ordinary promo codes
    "Stop judi online! Judol merusak keluarga, laporkan situs judi ke aduankonten.id",
    "Polisi tangkap bandar judi online di Medan, barang bukti 3 ponsel https://t.co/abc123",
    "Diskon THR 25% pakai kode THR25 di www.matahari.com sampai 31 Maret",
    "Slot jadwal konsultasi dosen masih ada hari Kamis, daftar lewat link di grup",
])
def test_rule_quiet_on_legit(text):
    assert [h.id for h in check(text)] == []


def test_api_returns_reasons_for_rule_hit():
    body = client.post("/v1/predict", json={"text": "Ini foto paket kakak ya: LIHAT_FOTO_PAKET.apk"}).json()
    assert body["label"] == "phishing"
    assert body["confidence"] >= 0.95
    assert any(".apk" in r for r in body["reasons"])


def test_api_no_reasons_for_legit():
    body = client.post("/v1/predict", json={"text": "Kode verifikasi WhatsApp Anda: 482-913. Jangan bagikan kode ini."}).json()
    assert body["label"] == "aman"
    assert body["reasons"] == []


def test_api_flags_user_reported_judol_message():
    text = "Ke cici01 peener1ma THR 275.000! akaligabandar.mom aambil skrg pkai k0dee : PUASA2026"
    body = client.post("/v1/predict", json={"text": text}).json()
    assert body["label"] == "phishing"
    assert any("judi online" in r for r in body["reasons"])


def test_api_judol_model_flags_promo_without_rule_hit():
    # no domain/link -> the online_gambling rule stays quiet; the judol detector model must catch it
    text = "Situs paling gacor hari ini, modal receh bisa maxwin, buruan main sekarang bosku"
    assert "online_gambling" not in [h.id for h in check(text)]
    body = client.post("/v1/predict", json={"text": text}).json()
    assert body["label"] == "phishing"
    assert any("judi online" in r for r in body["reasons"])
