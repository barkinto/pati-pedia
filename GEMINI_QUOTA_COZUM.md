# 🔧 Gemini API Quota Sorunu Çözüm Rehberi

Eğer 1 haftadır "API quota limiti aşıldı" hatası alıyorsanız ve yeni key açsanız bile aynı hatayı alıyorsanız, aşağıdaki çözümleri deneyin:

## 🎯 Hızlı Çözümler

### 1. ✅ Cache ve Rate Limiting Eklendi (Otomatik)
Projeye **cache mekanizması** ve **rate limiting** eklendi:
- Aynı kedi cinsi için tekrar API çağrısı yapılmaz (24 saat cache)
- API çağrıları arasında minimum 2 saniye bekleme (quota'yı korur)
- Bu sayede gereksiz API çağrıları azalır

### 2. 🔑 Farklı Google Hesabı ile Yeni Proje Oluşturun

**Sorun:** Aynı Google hesabı/proje altında key açıyorsanız, quota paylaşılıyor olabilir.

**Çözüm:**
1. **Yeni bir Google hesabı oluşturun** (veya farklı bir hesap kullanın)
2. **Google AI Studio'ya gidin:** https://aistudio.google.com/app/apikey
3. **Yeni hesabınızla giriş yapın**
4. **"Create API Key" butonuna tıklayın**
5. **Yeni key'i kopyalayın**

### 3. 📊 Google Cloud Console'da Quota Kontrolü

1. **Google Cloud Console'a gidin:** https://console.cloud.google.com/
2. **API'ler ve Servisler > Kotalar** bölümüne gidin
3. **"Generative Language API"** için quota limitlerini kontrol edin
4. **Günlük/aylık limitlerinizi** kontrol edin
5. Gerekirse **quota artırma talebi** gönderin

### 4. 💳 Billing Hesabı Kontrolü

**Ücretsiz tier limitleri:**
- Gemini API ücretsiz tier'da **günlük 15 RPM (requests per minute)** limiti var
- Aylık toplam istek sayısı da sınırlı olabilir

**Çözüm:**
1. **Google Cloud Console > Billing** bölümüne gidin
2. **Billing hesabınızın aktif** olduğundan emin olun
3. Gerekirse **ücretli plana geçin** (daha yüksek limitler)

### 5. 🔄 API Key'i Tamamen Silip Yeniden Oluşturun

1. **Google AI Studio'da mevcut key'i silin**
2. **Birkaç saat bekleyin** (quota reset olması için)
3. **Yeni bir key oluşturun**
4. **Yeni key'i projeye ekleyin**

### 6. 📝 API Key'i Projeye Ekleme

**Yöntem 1: Environment Variable (Önerilen)**
```bash
# macOS/Linux
export GEMINI_API_KEY="YENİ_API_KEY_BURAYA"
python3 api.py

# Windows (PowerShell)
$env:GEMINI_API_KEY="YENİ_API_KEY_BURAYA"
python api.py
```

**Yöntem 2: start_api.sh dosyasını düzenleyin**
```bash
# start_api.sh dosyasını açın
nano start_api.sh

# GEMINI_API_KEY değerini güncelleyin
export GEMINI_API_KEY="YENİ_API_KEY_BURAYA"
```

**Yöntem 3: api.py dosyasında güncelleyin**
```python
# api.py dosyasında (satır 329 ve 470)
api_key = os.getenv('GEMINI_API_KEY', 'YENİ_API_KEY_BURAYA')
```

## 🚨 Yaygın Hatalar ve Çözümleri

### "API quota limiti aşıldı" - Yeni key açsam bile
- **Sebep:** Aynı Google hesabı/proje altında key açıyorsunuz
- **Çözüm:** Farklı bir Google hesabı ile yeni proje oluşturun

### "API key geçersiz"
- **Sebep:** Key yanlış kopyalandı veya silindi
- **Çözüm:** Google AI Studio'da yeni key oluşturun ve doğru kopyalayın

### "Rate limit exceeded"
- **Sebep:** Çok hızlı istek gönderiyorsunuz
- **Çözüm:** Rate limiting eklendi (otomatik 2 saniye bekleme)

## 📈 Quota Limitleri (Gemini API)

**Ücretsiz Tier:**
- 15 RPM (requests per minute)
- Günlük limit: ~1,000-2,000 istek (değişebilir)
- Aylık limit: ~50,000 istek (değişebilir)

**Ücretli Plan:**
- Daha yüksek limitler
- Daha fazla istek hakkı

## 💡 İpuçları

1. **Cache kullanın:** Aynı cins için tekrar API çağrısı yapmayın (otomatik eklendi)
2. **Rate limiting:** Çok hızlı istek göndermeyin (otomatik eklendi)
3. **Farklı hesap:** Yeni Google hesabı ile deneyin
4. **Billing:** Ücretli plana geçmeyi düşünün
5. **Quota kontrolü:** Google Cloud Console'da quota durumunu kontrol edin

## 🔍 Quota Durumunu Kontrol Etme

Terminal'de test edin:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: YENİ_API_KEY_BURAYA' \
  -X POST \
  -d '{
    "contents": [{
      "parts": [{
        "text": "Merhaba"
      }]
    }]
  }'
```

Eğer `429` hatası alıyorsanız, quota aşılmış demektir.

## ✅ Başarılı Test

Eğer şu şekilde bir response alıyorsanız, API çalışıyor demektir:
```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "text": "..."
      }]
    }
  }]
}
```

## 🆘 Hala Çalışmıyorsa

1. **Farklı bir Google hesabı** ile yeni proje oluşturun
2. **Google Cloud Console'da** quota durumunu kontrol edin
3. **Billing hesabınızın aktif** olduğundan emin olun
4. **Birkaç saat bekleyin** (quota reset olması için)
5. **Google AI Studio'da** yeni key oluşturun

---

**Not:** Cache ve rate limiting özellikleri projeye eklendi. Bu sayede gereksiz API çağrıları azalacak ve quota daha verimli kullanılacak.

