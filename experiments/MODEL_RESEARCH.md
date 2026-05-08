# Riset Model AI untuk Receipt Parsing

## Tanggal: 8 Mei 2026
## Tujuan: Menemukan model AI OCR-free terbaik untuk ekstraksi data struk belanja

---

## Kriteria Pemilihan Model

1. **OCR-Free**: Model harus bisa membaca dokumen tanpa OCR tradisional (EasyOCR/PyTesseract)
2. **Akurasi**: Mampu mengekstrak data dengan akurat
3. **Kecepatan**: Inference time yang reasonable
4. **Kemudahan Implementasi**: Mudah diintegrasikan
5. **Resource Requirements**: Bisa jalan di CPU atau GPU consumer-grade

---

## Model Kandidat

### 1. Donut (Document Understanding Transformer)
**Repository**: `naver-clova-ix/donut-base-finetuned-cord-v2`

**Deskripsi**:
- End-to-end document understanding model
- OCR-free architecture
- Pre-trained pada CORD dataset (receipts)
- Transformer-based

**Kelebihan**:
- Sudah fine-tuned untuk receipts
- End-to-end processing
- Good accuracy untuk structured documents
- Open source dan gratis

**Kekurangan**:
- Membutuhkan GPU untuk inference cepat
- Model size cukup besar (~500MB)
- Perlu preprocessing gambar

**Resource Requirements**:
- RAM: ~4GB
- GPU: Optional tapi recommended
- Model Size: ~500MB

**Expected Performance**:
- Inference Time (CPU): 5-10 detik
- Inference Time (GPU): 1-3 detik
- Accuracy: High untuk receipts

---

### 2. GPT-4 Vision API (OpenAI)
**API**: OpenAI GPT-4 Vision

**Deskripsi**:
- Multimodal LLM dengan vision capabilities
- Dapat memahami dan mengekstrak informasi dari gambar
- Prompt-based extraction

**Kelebihan**:
- Sangat akurat
- Mudah implementasi (API call)
- Tidak perlu GPU lokal
- Flexible dengan prompt engineering
- Bisa handle berbagai format struk

**Kekurangan**:
- Berbayar (per API call)
- Membutuhkan internet connection
- Latency tergantung network
- Rate limiting

**Resource Requirements**:
- RAM: Minimal (hanya untuk API call)
- GPU: Tidak perlu
- Internet: Required

**Expected Performance**:
- Inference Time: 2-5 detik (tergantung network)
- Accuracy: Very High
- Cost: ~$0.01-0.03 per image

---

### 3. LayoutLMv3 (Microsoft) - Alternatif
**Repository**: `microsoft/layoutlmv3-base`

**Deskripsi**:
- Multimodal pre-training untuk document understanding
- Combines text, layout, and image information
- State-of-the-art untuk document AI

**Kelebihan**:
- Very high accuracy
- Good untuk complex layouts
- Pre-trained pada banyak document types

**Kekurangan**:
- Perlu fine-tuning untuk receipt-specific tasks
- Lebih complex untuk setup
- Membutuhkan OCR preprocessing (Tesseract)

**Status**: Backup option jika Donut tidak perform well

---

### 4. TrOCR + Layout Analysis - Alternatif
**Repository**: `microsoft/trocr-base-printed`

**Deskripsi**:
- Transformer-based OCR
- Bisa dikombinasi dengan layout detection

**Kelebihan**:
- Good text recognition
- Pre-trained untuk printed text

**Kekurangan**:
- Perlu layout detection terpisah
- Multi-step process
- Lebih complex pipeline

**Status**: Backup option

---

## Pilihan Model untuk Eksperimen

### Model 1: Donut (Local)
**Alasan**:
- Sudah fine-tuned untuk receipts
- Open source dan gratis
- Bisa jalan offline
- Good balance antara accuracy dan practicality

### Model 2: GPT-4 Vision API
**Alasan**:
- State-of-the-art accuracy
- Mudah implementasi
- Flexible dengan prompt engineering
- Good untuk comparison dengan local model

---

## Rencana Eksperimen

### Setup
1. Install dependencies untuk kedua model
2. Siapkan 2 foto struk untuk testing
3. Buat script untuk inference

### Testing
1. Test Donut dengan kedua struk
2. Test GPT-4 Vision dengan kedua struk
3. Catat hasil ekstraksi
4. Ukur waktu inference
5. Evaluasi akurasi

### Metrics
1. **Akurasi Ekstraksi**:
   - Item names
   - Quantities
   - Prices
   - Subtotal
   - Additional charges
   - Total

2. **Kecepatan**:
   - Inference time per image
   - Preprocessing time

3. **Kemudahan**:
   - Setup complexity
   - Code complexity
   - Maintenance

4. **Cost**:
   - Model size
   - API cost (untuk GPT-4)
   - Resource usage

---

## Expected Outcome

Setelah eksperimen, kita akan memilih model yang:
1. Paling akurat untuk use case kita
2. Reasonable inference time
3. Mudah di-maintain
4. Cost-effective

---

## Next Steps

1. ✅ Dokumentasi riset model
2. ⏳ Implementasi Donut parser
3. ⏳ Implementasi GPT-4 Vision parser
4. ⏳ Testing dengan sample receipts
5. ⏳ Analisis dan pemilihan model final
