# 🔧 Gemini API Quota Sorunu - Adım Adım Çözüm

## 🎯 Hızlı Çözüm

### Adım 1: Yeni API Key Alın

1. **Google AI Studio'ya gidin:**
   - https://aistudio.google.com/app/apikey

2. **ÖNEMLİ: Farklı bir Google hesabı kullanın!**
   - Aynı hesap altında key açıyorsanız quota paylaşılıyor olabilir
   - Tamamen farklı bir email ile yeni Google hesabı oluşturun

3. **Yeni hesapta:**
   - Telefon doğrulaması yapın (gerekirse)
   - "Create API Key" butonuna tıklayın
   - Key'i kopyalayın (örnek: `AIzaSy...`)

### Adım 2: Key'i Test Edin

```bash
./test_gemini_key.sh YOUR_NEW_API_KEY
```

**Başarılı test sonucu:**
```
✅ API Key ÇALIŞIYOR!
HTTP Status Code: 200
```

**Quota hatası:**
```
❌ QUOTA AŞILMIŞ!
HTTP Status Code: 429
```

### Adım 3: Key'i Projeye Ekleyin

**Yöntem 1: Otomatik Güncelleme (Önerilen)**
```bash
python3 update_api_key.py YOUR_NEW_API_KEY
```

**Yöntem 2: Manuel Güncelleme**

`start_api.sh` dosyasını düzenleyin:
```bash
nano start_api.sh
# GEMINI_API_KEY değerini güncelleyin
export GEMINI_API_KEY="YOUR_NEW_API_KEY"
```

`api.py` dosyasında 2 yerde güncelleyin (satır ~360 ve ~490):
```python
api_key = os.getenv('GEMINI_API_KEY', 'YOUR_NEW_API_KEY')
```

### Adım 4: Google Cloud Console Kontrolü

1. **Google Cloud Console'a gidin:**
   - https://console.cloud.google.com/

2. **API'yi Etkinleştirin:**
   - "API'ler ve Servisler > Kütüphane" bölümüne gidin
   - "Generative Language API" arayın
   - "Etkinleştir" butonuna tıklayın

3. **Billing Hesabı:**
   - "Faturalandırma" bölümüne gidin
   - Billing hesabınızın aktif olduğundan emin olun
   - Gerekirse yeni billing hesabı oluşturun

### Adım 5: Projeyi Yeniden Başlatın

```bash
# Mevcut process'i durdurun
pkill -f "api.py\|vite"

# Yeniden başlatın
python3 api.py
```

## 🚨 Hala Quota Hatası Alıyorsanız

### Çözüm 1: Tamamen Farklı Google Hesabı
- Farklı bir email ile yeni Google hesabı oluşturun
- Bu hesaptan yeni key oluşturun
- Telefon doğrulaması yapın
- Billing hesabı ekleyin

### Çözüm 2: Birkaç Saat Bekleyin
- Yeni hesaplarda bile bazı kısıtlamalar olabilir
- Birkaç saat bekleyip tekrar deneyin
- Quota limitleri günlük/aylık olarak reset olabilir

### Çözüm 3: Google Cloud Console'da Quota Kontrolü
1. Google Cloud Console'a gidin
2. "API'ler ve Servisler > Kotalar" bölümüne gidin
3. "Generative Language API" için quota durumunu kontrol edin
4. Gerekirse quota artırma talebi gönderin

## 💡 İpuçları

1. **Cache kullanın:** Aynı cins için tekrar API çağrısı yapılmaz (otomatik)
2. **Rate limiting:** API çağrıları arasında 2 saniye bekleme (otomatik)
3. **Farklı hesap:** Yeni Google hesabı ile deneyin
4. **Test edin:** Yeni key'i mutlaka test edin (`test_gemini_key.sh`)

## 📞 Yardım

Eğer hala sorun yaşıyorsanız:
1. `test_gemini_key.sh` scriptini çalıştırın ve sonucu paylaşın
2. Google Cloud Console'da API durumunu kontrol edin
3. Billing hesabı durumunu kontrol edin

