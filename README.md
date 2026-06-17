# TCO Analysis — Last-Mile Delivery Route Simulator

Simulasi komputasi yang membandingkan dua arsitektur algoritma pencarian rute kurir (*Last-Mile Delivery*) pada dua skenario ekonomi berbeda, untuk membuktikan kondisi finansial di mana masing-masing algoritma lebih menguntungkan.

---

## 1. Cara Menjalankan Program

### Persyaratan
- Python 3.8 atau lebih baru
- Koneksi internet aktif (untuk kalkulasi matriks jarak via OSRM API)

### Instalasi
```bash
pip install -r requirements.txt
```

### Langkah 1 — Generate Matriks Jarak (sekali saja)
Ubah koordinat lokasi di `data/lokasi.json` menjadi matriks jarak nyata (km) via OSRM API:
```bash
python src/main.py --calculate-graph
```
Perintah ini membuat file `data/generated/graph.csv`. Ulangi hanya jika ada perubahan lokasi.

### Langkah 2 — Jalankan Simulasi

**Bandingkan semua skenario sekaligus (direkomendasikan):**
```bash
python src/main.py
```

**Jalankan satu skenario tertentu:**
```bash
python src/main.py --scenario subsidi
python src/main.py --scenario krisis
```

**Output yang ditampilkan:**
- Urutan rute untuk setiap algoritma
- Total jarak tempuh (km)
- Waktu eksekusi presisi (detik)
- Biaya BBM, Biaya Komputasi Server, dan TCO
- Tabel komparasi lintas skenario + analisis break-even

---

## 2. Pemilihan Algoritma

### Algoritma A — Heuristik: Nearest Neighbor Greedy
**Cara kerja:** Dari hub, selalu kunjungi pelanggan terdekat yang belum dikunjungi, ulangi sampai semua terkunjungi, lalu kembali ke hub.

**Alasan dipilih:**
- Implementasi from-scratch sederhana dan mudah diaudit
- Kompleksitas O(n²) menjamin eksekusi sangat cepat untuk n berapa pun
- Representatif sebagai baseline heuristik "greedy" yang paling umum digunakan di industri last-mile

**Trade-off:** Tidak menjamin rute optimal — solusi bisa 15–25% lebih jauh dari optimal, tergantung distribusi titik.

### Algoritma B — Eksak: Branch and Bound (B&B) with Lower Bound Pruning
**Cara kerja:** Eksplorasi rekursif semua permutasi rute. Setiap cabang dipangkas (*pruned*) jika estimasi lower bound jarak sisanya sudah melebihi solusi terbaik yang sudah ditemukan.

**Alasan dipilih atas Held-Karp (DP):**
- B&B memiliki worst-case yang sama dengan brute force (O(n!)), namun pruning adaptif membuat B&B jauh lebih cepat dalam praktik pada dataset berukuran kecil-menengah (n ≤ 15)
- Held-Karp memiliki kompleksitas waktu *teoritis* lebih baik — O(n²·2ⁿ) — tetapi membutuhkan memori O(n·2ⁿ) yang tumbuh secara eksponensial
- Untuk n = 12 pelanggan: Held-Karp butuh 12² × 4096 = ~600K entries memori; B&B dengan pruning baik menyelesaikan dalam < 1 detik

**Trade-off:** Waktu eksekusi meledak secara eksponensial saat n membesar (> 20 pelanggan praktis tidak feasible tanpa optimasi tambahan).

---

## 3. Analisis Kompleksitas (Big-O)

| Algoritma | Waktu (Worst Case) | Waktu (Praktik) | Ruang |
|---|---|---|---|
| Nearest Neighbor Greedy | O(n²) | O(n²) | O(n) |
| Branch and Bound | O(n!) | Jauh lebih baik dengan pruning | O(n²) — stack rekursi |
| Held-Karp DP *(tidak dipakai)* | O(n²·2ⁿ) | O(n²·2ⁿ) | O(n·2ⁿ) |

**Derivasi loop/rekursi:**

**Greedy:**
```
for setiap pelanggan (n iterasi):          # O(n)
    for setiap pelanggan belum dikunjungi: # O(n)
        hitung jarak ke current node       # O(1)
=> Total: O(n²)
```

**Branch and Bound:**
```
_backtrack(current, visited_mask, path, dist):
    for setiap pelanggan belum dikunjungi: # O(n) cabang
        hitung lower_bound:                # O(n)
        if bound < best: rekursi          # kedalaman rekursi = n
=> Worst case: O(n) × O(n) × n! = O(n! × n²), dipangkas oleh pruning
```

Pada dataset ini (n = 12): Greedy selesai dalam ~0.00005 detik; B&B dalam ~0.5 detik.

---

## 4. Summary — Keputusan Bisnis

### Hasil Simulasi

| | Subsidi (Rp 5.000/L) | Krisis (Rp 20.000/L) |
|---|---|---|
| **Greedy — Jarak** | 31.07 km | 31.07 km |
| **Greedy — TCO** | Rp 5.238 | Rp 20.946 |
| **Exact B&B — Jarak** | 29.48 km | 29.48 km |
| **Exact B&B — TCO** | Rp 29.007 | Rp 47.077 |
| **Rekomendasi** | **Greedy** | **Greedy** |

### Kesimpulan

**Pada kedua skenario, Heuristic Greedy lebih menguntungkan secara TCO.**

Meskipun algoritma eksak (B&B) menghasilkan rute ~5% lebih pendek (29.48 km vs 31.07 km), penghematan BBM tersebut tidak cukup untuk menutup biaya komputasi server yang sangat tinggi. Dengan sistem *pay-as-you-go* Rp 50/ms, waktu eksekusi B&B (~500ms) menghasilkan tagihan server **±Rp 25.000 per pengiriman** — jauh lebih besar dari selisih biaya BBM sekitar Rp 170 (subsidi) hingga Rp 686 (krisis).

### Titik Break-Even

```
Break-even tercapai saat:  TCO_exact = TCO_greedy
Selisih konsumsi BBM    :  ±0.034 liter (Greedy lebih boros)
Selisih biaya komputasi :  ±Rp 25.378 (Exact lebih mahal)

Break-even harga BBM = Rp 25.378 / 0.034 liter ≈ Rp 740.000/liter
```

**Algoritma eksak baru menguntungkan secara finansial jika harga BBM melebihi ±Rp 740.000/liter** — sebuah angka yang tidak realistis dalam kondisi ekonomi normal maupun krisis sekalipun.

**Rekomendasi final:** Pertahankan algoritma Heuristic Greedy untuk operasional sehari-hari. Investasi pada algoritma eksak hanya masuk akal jika biaya komputasi server turun drastis (misalnya migrasi ke on-premise server dengan biaya tetap) atau jika jumlah pelanggan per rute berkurang secara signifikan sehingga waktu eksekusi mendekati nol.
