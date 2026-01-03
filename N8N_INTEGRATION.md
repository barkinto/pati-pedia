  # 🔗 n8n Entegrasyonu - Kedi Fotoğraf Analizi

Bu API, n8n workflow'larında kullanılmak üzere kedi fotoğrafı analizi yapabilir.

## 📡 API Endpoints

### 1. Kedi Cinsi Tahmini + Görsel Analizi
**POST** `/api/predict`

**Request (multipart/form-data):**
- `image`: Image file
- `skip_detection`: "true" veya "false" (opsiyonel)

**Response:**
```json
{
  "success": true,
  "predictions": [
    {
      "breed": "Persian",
      "confidence": 85.23
    }
  ],
  "cat_detection": {
    "detected": true,
    "confidence": 92.5,
    "message": "Kedi tespit edildi"
  },
  "cat_analysis": {
    "age_estimate": "Yetişkin (2-5 yaş)",
    "health_status": "Sağlıklı görünüyor",
    "physical_features": "...",
    "behavior_notes": "...",
    "care_recommendations": "..."
  }
}
```

### 2. Sadece Görsel Analizi
**POST** `/api/analyze-cat`

**Request Options:**

**A) File Upload (multipart/form-data):**
- `image`: Image file
- `breed`: Kedi cinsi (opsiyonel)

**B) Base64 (application/json):**
```json
{
  "image_base64": "base64_encoded_image_string",
  "breed": "Persian"
}
```

**Response:**
```json
{
  "success": true,
  "analysis": "Yaş tahmini: Yetişkin... Sağlık: Sağlıklı görünüyor...",
  "breed": "Persian"
}
```

## 🔧 n8n Workflow Örneği

### Senaryo 1: WhatsApp'tan Gelen Fotoğrafı Analiz Et

1. **Webhook Trigger** (WhatsApp webhook)
2. **HTTP Request Node** → `/api/predict`
   - Method: POST
   - Body: Form-Data
   - Image: `{{ $json.image }}`
3. **Function Node** → Sonuçları formatla
4. **HTTP Request Node** → `/api/analyze-cat` (detaylı analiz için)
5. **Send Message** → Sonuçları kullanıcıya gönder

### Senaryo 2: E-posta ile Fotoğraf Analizi

1. **Email Trigger** (Gmail/IMAP)
2. **Extract Attachment**
3. **HTTP Request Node** → `/api/predict`
4. **HTTP Request Node** → `/api/breed-info` (cins bilgisi)
5. **HTTP Request Node** → `/api/analyze-cat` (görsel analiz)
6. **Send Email** → Detaylı rapor gönder

## 📋 n8n HTTP Request Node Ayarları

### Predict Endpoint:
```
URL: http://localhost:5001/api/predict
Method: POST
Body Type: Form-Data
Fields:
  - image: (File) {{ $json.image }}
  - skip_detection: false
```

### Analyze Cat Endpoint (Base64):
```
URL: http://localhost:5001/api/analyze-cat
Method: POST
Headers:
  Content-Type: application/json
Body:
{
  "image_base64": "{{ $json.imageBase64 }}",
  "breed": "{{ $json.breed }}"
}
```

## 🎯 Analiz Çıktıları

Gemini AI görsel analizi şunları içerir:
- **Yaş Tahmini:** Yavru/Genç/Yetişkin/Yaşlı
- **Sağlık Durumu:** Genel görünüm değerlendirmesi
- **Fiziksel Özellikler:** Vücut yapısı, tüy durumu
- **Davranış İpuçları:** Fotoğraftan çıkarılabilecek özellikler
- **Bakım Önerileri:** Özel öneriler

## 🔐 Güvenlik

- API key'i environment variable olarak saklayın
- Production'da HTTPS kullanın
- Rate limiting ekleyin (opsiyonel)

## 📝 Örnek cURL Komutları

```bash
# Tahmin + Analiz
curl -X POST http://localhost:5001/api/predict \
  -F "image=@cat.jpg" \
  -F "skip_detection=false"

# Sadece Analiz (Base64)
curl -X POST http://localhost:5001/api/analyze-cat \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "base64_string_here",
    "breed": "Persian"
  }'
```

