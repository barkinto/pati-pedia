# 🔍 API Key Sorun Giderme Rehberi

## ❓ "Yeni hesaptan key ekledim ama hala quota hatası alıyorum"

Bu durumda birkaç olası neden var:

### 1. ✅ Key Doğru Yere Eklenmemiş Olabilir

**Sorun:** Yeni key'i eklediniz ama proje hala eski key'i kullanıyor.

**Çözüm:**
```bash
# Otomatik güncelleme scriptini kullanın
python3 update_api_key.py YOUR_NEW_API_KEY

# Veya manuel olarak:
# 1. api.py dosyasında 2 yerde (satır ~350 ve ~483)
# 2. start_api.sh dosyasında
```

### 2. 🔑 Key Test Edilmemiş Olabilir

**Sorun:** Key çalışmıyor olabilir.

**Çözüm:**
```bash
# Key'i test edin
./test_gemini_key.sh YOUR_NEW_API_KEY
```

**Beklenen sonuç:**
- ✅ HTTP 200: Key çalışıyor
- ❌ HTTP 429: Quota aşılmış
- ❌ HTTP 401/403: Key geçersiz

### 3. 🆕 Yeni Hesap İçin Bile Kısıtlamalar Olabilir

**Sorun:** Google'ın yeni hesaplar için de bazı kısıtlamaları var.

**Olası nedenler:**
- **Telefon doğrulaması yapılmamış:** Yeni hesaplarda telefon doğrulaması gerekebilir
- **Billing hesabı aktif değil:** Ücretsiz tier için bile billing hesabı gerekebilir
- **API etkinleştirilmemiş:** Google Cloud Console'da API etkinleştirilmemiş olabilir

**Çözüm:**
1. **Google AI Studio'da:**
   - Hesap ayarlarını kontrol edin
   - Telefon doğrulaması yapın (gerekirse)
   - Billing hesabını kontrol edin

2. **Google Cloud Console'da:**
   - https://console.cloud.google.com/ adresine gidin
   - "API'ler ve Servisler > Kütüphane" bölümüne gidin
   - "Generative Language API" arayın
   - "Etkinleştir" butonuna tıklayın

### 4. 💳 Billing Hesabı Sorunu

**Sorun:** Ücretsiz tier için bile billing hesabı gerekebilir.

**Çözüm:**
1. Google Cloud Console'a gidin
2. "Faturalandırma" bölümüne gidin
3. Billing hesabınızın aktif olduğundan emin olun
4. Gerekirse yeni billing hesabı oluşturun

### 5. 🔄 Desktop App Environment Variable Sorunu

**Sorun:** `desktop_app.py` çalışırken environment variable set edilmemiş.

**Çözüm:**
- `desktop_app.py` güncellendi, artık `start_api.sh`'den key'i otomatik okuyor
- Veya environment variable'ı manuel set edin:
```bash
export GEMINI_API_KEY="YOUR_NEW_API_KEY"
python3 desktop_app.py
```

### 6. 🧪 Key Doğru Oluşturulmamış Olabilir

**Sorun:** Key oluşturulurken bir hata olmuş olabilir.

**Kontrol:**
1. Google AI Studio'da key'inizi kontrol edin
2. Key'in aktif olduğundan emin olun
3. Key'in silinmediğinden emin olun

## 🎯 Adım Adım Çözüm

### Adım 1: Key'i Test Edin
```bash
./test_gemini_key.sh YOUR_NEW_API_KEY
```

### Adım 2: Key'i Projeye Ekleyin
```bash
python3 update_api_key.py YOUR_NEW_API_KEY
```

### Adım 3: Google Cloud Console Kontrolü
1. https://console.cloud.google.com/ adresine gidin
2. "API'ler ve Servisler > Kütüphane" bölümüne gidin
3. "Generative Language API" arayın
4. "Etkinleştir" butonuna tıklayın (eğer etkin değilse)

### Adım 4: Billing Hesabı Kontrolü
1. Google Cloud Console'da "Faturalandırma" bölümüne gidin
2. Billing hesabınızın aktif olduğundan emin olun
3. Gerekirse yeni billing hesabı oluşturun

### Adım 5: Projeyi Yeniden Başlatın
```bash
pkill -f "desktop_app|api.py"
python3 desktop_app.py
```

## 🚨 Hala Çalışmıyorsa

### Alternatif 1: Tamamen Farklı Bir Google Hesabı
- Farklı bir email adresi ile yeni Google hesabı oluşturun
- Bu hesaptan yeni key oluşturun
- Telefon doğrulaması yapın
- Billing hesabı ekleyin

### Alternatif 2: Google Cloud Console'da Quota Kontrolü
1. Google Cloud Console'a gidin
2. "API'ler ve Servisler > Kotalar" bölümüne gidin
3. "Generative Language API" için quota durumunu kontrol edin
4. Quota limitlerini kontrol edin
5. Gerekirse quota artırma talebi gönderin

### Alternatif 3: Birkaç Saat Bekleyin
- Yeni hesaplarda bile bazı kısıtlamalar olabilir
- Birkaç saat bekleyip tekrar deneyin
- Quota limitleri günlük/aylık olarak reset olabilir

## 💡 İpuçları

1. **Key'i mutlaka test edin** (`test_gemini_key.sh`)
2. **Google Cloud Console'da API'yi etkinleştirin**
3. **Billing hesabını kontrol edin**
4. **Telefon doğrulaması yapın** (yeni hesaplarda)
5. **Farklı bir Google hesabı deneyin** (son çare)

## 📞 Yardım

Eğer hala sorun yaşıyorsanız:
1. `test_gemini_key.sh` scriptini çalıştırın ve sonucu paylaşın
2. Google Cloud Console'da API durumunu kontrol edin
3. Billing hesabı durumunu kontrol edin
4. `update_api_key.py` scriptini çalıştırıp key'i güncelleyin

---

**Not:** `desktop_app.py` güncellendi, artık `start_api.sh`'den key'i otomatik okuyor. Bu sayede key güncellemeleri daha kolay olacak.

