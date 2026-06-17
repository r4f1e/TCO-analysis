# Petunjuk Penggunaan Program 

Dokumentasi ini mencakup instruksi instalasi, persiapan data, hingga eksekusi program.

## 1. Persyaratan Sistem
* Python 3.8 atau versi lebih baru.
* Koneksi internet aktif (untuk menghubungi *endpoint* API OSRM).

## 2. Instalasi
Buka terminal dan arahkan ke *root* direktori proyek Anda. Instal dependensi eksternal yang dibutuhkan melalui perintah berikut:

```bash
pip install -r requirements.txt
```

## 3. Generate Data (Kalkulasi Matriks Jarak)
Sebelum menjalankan pencarian rute, Anda **wajib** mengubah titik koordinat yang ada di `lokasi.json` menjadi matriks jarak melalui bantuan OSRM API untuk mendapatkan jarak sebenarnya. Eksekusi perintah CLI berikut:

```bash
python src/main.py --calculate-graph
```
**Catatan:** Kode ini akan membuat file `data/generated/graph.csv`. Langkah ini hanya perlu dilakukan satu kali, atau diulangi hanya jika ada perubahan/penambahan lokasi baru di file `lokasi.json`.

## 4. Menjalankan Simulasi Program (SEMENTARA BELUM ADA OPSI SKENARIO)
Setelah matriks jarak berhasil digenerate, pastikan file `customer.json` sudah berisi daftar pelanggan yang valid. Untuk menjalankan komparasi rute dan perhitungan jarak, gunakan perintah:

```bash
python src/main.py
```
**Output:** Terminal akan memuat data, memvalidasinya, dan mengeksekusi algoritma heuristik dan exact.