# MediaDownloader - Standalone Premium App

MediaDownloader adalah aplikasi pengunduh media (video/audio) mandiri yang dirancang dengan estetika premium dan performa tinggi. Aplikasi ini memungkinkan Anda mengunduh konten dari 1000+ platform termasuk YouTube, TikTok, Instagram, Facebook, dan lainnya.

## Fitur Utama
- **Universal Downloader**: Didukung oleh `yt-dlp` untuk dukungan platform terluas.
- **Premium UI**: Antarmuka berbasis React dengan *Glassmorphism*, utilitas styling dari *Tailwind CSS v4*, dan animasi halus menggunakan *Framer Motion*.
- **Real-time Tracking**: Lihat kecepatan download, persentase, dan estimasi waktu secara langsung via teknologi SSE.
- **Browser-side Download**: Setelah proses download selesai di backend, browser akan otomatis memicu jendela **"Save As"** untuk menyimpan file ke lokasi pilihanmu.
- **High Quality**: Pilihan format lengkap dari 144p hingga resolusi maksimal.

## Arsitektur Project
- **Frontend**: React (Vite) + Tailwind CSS + Framer Motion + Lucide React + Axios.
- **Backend**: FastAPI (Python) + SQLAlchemy (SQLite) + yt-dlp.

---

## 🚀 Cara Menghidupkan Project (Quick Start)

Gunakan langkah ini setiap kali kamu ingin menjalankan aplikasi setelah instalasi awal selesai:

### 1. Jalankan Backend (Mesin)
1. Buka terminal, pastikan di folder `d:\MediaDownloader`.
2. Jalankan perintah:
   ```powershell
   python api/main.py
   ```
   *Biarkan terminal ini tetap terbuka selama penggunaan.*

### 2. Jalankan Frontend (Tampilan)
1. Buka terminal **baru**.
2. Masuk ke folder frontend:
   ```powershell
   cd frontend
   ```
3. Jalankan perintah:
   ```powershell
   npm run dev
   ```

### 3. Buka di Browser
Buka alamat berikut di browser kamu:
👉 **[http://localhost:5173](http://localhost:5173)**

---

## 📦 Panduan Instalasi (Hanya sekali di awal)

### 1. Persiapan Backend
```powershell
cd d:\MediaDownloader
pip install -r requirements.txt
```

### 2. Persiapan Frontend
```powershell
cd d:\MediaDownloader\frontend
npm install
npm install framer-motion lucide-react axios
npm install -D tailwindcss @tailwindcss/postcss
```

---

## 💡 Troubleshooting & FAQ

**1. Error: `ModuleNotFoundError: No module named 'core'`**
Jalankan `python api/main.py` dari folder root `d:\MediaDownloader`, bukan dari dalam folder `api`.

**2. Error: `Backend Error: Request failed with status code 405`**
Ini biasanya karena tabrakan port. Pastikan kamu sudah menggunakan port `8888` di `api/main.py` dan mematikan proses python yang lama sebelum menjalankan yang baru.

**3. Lokasi File Sementara**
Aplikasi ini mendownload file ke folder *Temp* sistem sebelum dikirim ke browser. File ini akan otomatis dibersihkan oleh sistem operasi secara berkala.

---
*Dikembangkan oleh Antigravity untuk kemudahan pengunduhan media.*
