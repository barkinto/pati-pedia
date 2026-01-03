# 🔑 Yeni Gemini API Key Ekleme Rehberi

## 📋 Adım 1: Yeni API Key Oluşturun

### 1.1. Google AI Studio'ya Gidin
- **Link:** https://aistudio.google.com/app/apikey
- Veya: https://makersuite.google.com/app/apikey

### 1.2. Giriş Yapın
- **ÖNEMLİ:** Farklı bir Google hesabı kullanın (quota sorunu için)
- Eğer aynı hesabı kullanıyorsanız, yeni bir Google hesabı oluşturun

### 1.3. API Key Oluşturun
1. **"Create API Key"** butonuna tıklayın
2. Proje seçin (veya yeni proje oluşturun)
3. **API Key'inizi kopyalayın** (örnek: `AIzaSy...`)

## 📋 Adım 2: API Key'i Test Edin

Terminal'de test scriptini çalıştırın:

```bash
# Yöntem 1: Script ile test
./test_gemini_key.sh YOUR_NEW_API_KEY

# Yöntem 2: Environment variable ile
export GEMINI_API_KEY="YOUR_NEW_API_KEY"
./test_gemini_key.sh
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

## 📋 Adım 3: API Key'i Projeye Ekleyin

### Yöntem 1: start_api.sh Dosyasını Düzenleyin (Önerilen)

```bash
# Dosyayı açın
nano start_api.sh

# GEMINI_API_KEY değerini güncelleyin
export GEMINI_API_KEY="YENİ_API_KEY_BURAYA"
```

### Yöntem 2: api.py Dosyasını Düzenleyin

`api.py` dosyasında 2 yerde güncelleme yapın:

**Satır ~329 (get_breed_info_from_gemini fonksiyonu):**
```python
api_key = os.getenv('GEMINI_API_KEY', 'YENİ_API_KEY_BURAYA')
```

**Satır ~480 (analyze_cat_image_with_gemini fonksiyonu):**
```python
api_key = os.getenv('GEMINI_API_KEY', 'YENİ_API_KEY_BURAYA')
```

### Yöntem 3: Environment Variable Olarak (Kalıcı)

**macOS/Linux:**
```bash
# ~/.zshrc veya ~/.bashrc dosyasına ekleyin
echo 'export GEMINI_API_KEY="YENİ_API_KEY_BURAYA"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (PowerShell):**
```powershell
# Sistem ortam değişkeni olarak ekleyin
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'YENİ_API_KEY_BURAYA', 'User')
```

## 📋 Adım 4: Projeyi Yeniden Başlatın

```bash
# Mevcut process'i durdurun
pkill -f "desktop_app\|api.py"

# Yeniden başlatın
python3 desktop_app.py
```

## ✅ Test Edin

1. Uygulamayı açın
2. Bir kedi fotoğrafı yükleyin
3. "Tahmin Et" butonuna tıklayın
4. Gemini AI bölümünün çalıştığını kontrol edin

## 🚨 Hala Quota Hatası Alıyorsanız

### Çözüm 1: Farklı Google Hesabı
- **Kesin çözüm:** Tamamen farklı bir Google hesabı ile yeni key oluşturun
- Aynı hesap altında key açıyorsanız, quota paylaşılıyor olabilir

### Çözüm 2: Birkaç Saat Bekleyin
- Quota limitleri günlük/aylık olarak reset olabilir
- Birkaç saat sonra tekrar deneyin

### Çözüm 3: Google Cloud Console Kontrolü
1. https://console.cloud.google.com/ adresine gidin
2. **API'ler ve Servisler > Kotalar** bölümüne gidin
3. **"Generative Language API"** için quota durumunu kontrol edin
4. Gerekirse **quota artırma talebi** gönderin

### Çözüm 4: Billing Hesabı
- Ücretsiz tier limitleri düşük olabilir
- Google Cloud Console'da billing hesabınızın aktif olduğundan emin olun
- Gerekirse ücretli plana geçin

## 💡 İpuçları

1. **Cache kullanın:** Aynı cins için tekrar API çağrısı yapılmaz (otomatik)
2. **Rate limiting:** API çağrıları arasında 2 saniye bekleme (otomatik)
3. **Farklı hesap:** Yeni Google hesabı ile deneyin
4. **Test edin:** Yeni key'i mutlaka test edin (`test_gemini_key.sh`)

## 📞 Yardım

Eğer hala sorun yaşıyorsanız:
1. `test_gemini_key.sh` scriptini çalıştırın
2. HTTP status code'u kontrol edin
3. `GEMINI_QUOTA_COZUM.md` dosyasına bakın

---

**Not:** Cache ve rate limiting özellikleri projeye eklendi. Bu sayede gereksiz API çağrıları azalacak ve quota daha verimli kullanılacak.

