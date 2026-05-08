# Panduan Eksperimen Model AI

## Persiapan

### 1. Install Dependencies

Pastikan virtual environment sudah aktif, lalu install dependencies:

```bash
# Aktifkan virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note**: PyTorch akan download ~2GB. Jika hanya punya CPU, bisa install versi CPU-only:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 2. Setup API Key (Opsional untuk GPT-4 Vision)

Jika ingin test GPT-4 Vision:

1. Buat file `.env` di root project
2. Tambahkan API key:
```
OPENAI_API_KEY=your_api_key_here
```

### 3. Siapkan Foto Struk

Tambahkan minimal 2 foto struk ke folder `data/`:
- Format: `.jpg`, `.jpeg`, atau `.png`
- Pastikan foto jelas dan tidak blur
- Lihat `data/README.md` untuk tips foto yang baik

## Menjalankan Eksperimen

### Opsi 1: Script Otomatis (Recommended)

```bash
python experiments/run_experiment.py
```

Script ini akan:
1. Detect semua foto struk di folder `data/`
2. Tanya model mana yang ingin ditest
3. Jalankan inference untuk setiap struk
4. Tampilkan hasil dan perbandingan
5. Simpan hasil ke `experiments/results/`

### Opsi 2: Test Model Individual

#### Test Donut:
```bash
python models/donut_parser.py
```

#### Test GPT-4 Vision:
```bash
python models/gpt4_vision_parser.py
```

### Opsi 3: Manual di Python

```python
from PIL import Image
from models.donut_parser import DonutReceiptParser

# Load image
image = Image.open("data/receipt_1.jpg")

# Initialize parser
parser = DonutReceiptParser()
parser.load_model()

# Parse receipt
result = parser.parse_receipt(image)

# Print results
print(result)
```

## Hasil Eksperimen

Hasil akan disimpan di `experiments/results/` dalam format JSON:

```json
{
  "receipt_name": "receipt_1",
  "timestamp": "2026-05-08 14:30:00",
  "donut": {
    "items": [...],
    "subtotal": 100.00,
    "total": 110.00,
    "inference_time": 3.45
  },
  "gpt4_vision": {
    "items": [...],
    "subtotal": 100.00,
    "total": 110.00,
    "inference_time": 2.15
  }
}
```

## Troubleshooting

### Error: CUDA out of memory
- Donut membutuhkan GPU memory. Jika tidak ada GPU atau memory tidak cukup, model akan otomatis pakai CPU (lebih lambat tapi tetap jalan)

### Error: 0penAI API key not found
- Pastikan file `.env` ada dan berisi `OPENAI_API_KEY`
- Atau skip GPT-4 Vision dan test Donut saja

### Error: No module named 'transformers'
- Jalankan: `pip install -r requirements.txt`

### Model download lambat
- Donut model ~500MB, akan download otomatis saat pertama kali dijalankan
- Pastikan koneksi internet stabil

## Metrics yang Diukur

1. **Akurasi Ekstraksi**:
   - Jumlah items yang terdeteksi
   - Akurasi nama item
   - Akurasi harga dan quantity
   - Akurasi subtotal dan total

2. **Kecepatan**:
   - Inference time (detik)
   - Preprocessing time

3. **Kemudahan**:
   - Setup complexity
   - Code complexity

4. **Cost**:
   - Model size (Donut)
   - API cost (GPT-4 Vision)

## Next Steps

Setelah eksperimen selesai:
1. Analisis hasil di `experiments/results/`
2. Bandingkan akurasi dan kecepatan
3. Pilih model terbaik untuk implementasi
4. Dokumentasi di README.md

---

**Happy Experimenting! 🚀**
