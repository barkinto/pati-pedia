# 🔑 Gemini API Key Kurulum Rehberi

## 1️⃣ API Key Alma

1. **Google AI Studio'ya gidin:**
   - 👉 https://aistudio.google.com/app/apikey
   - Google hesabınızla giriş yapın

2. **"Get API Key" veya "Create API Key" butonuna tıklayın**

3. **Proje seçin** (yoksa yeni proje oluşturun)

4. **API key'inizi kopyalayın** (AIzaSy... ile başlar)

## 2️⃣ API Key'i Ayarlama

### ✅ Yöntem 1: start_api.sh dosyasını düzenleyin (Önerilen)

`start_api.sh` dosyasını açın ve 4. satırdaki API key'i kendi key'inizle değiştirin:

```bash
export GEMINI_API_KEY="BURAYA-KENDI-API-KEY-INIZI-YAZIN"
```

Sonra API'yi başlatın:
```bash
./start_api.sh
```

### ✅ Yöntem 2: Terminal'de direkt kullanın

```bash
export GEMINI_API_KEY="BURAYA-KENDI-API-KEY-INIZI-YAZIN"
cd /Users/aliefeyilmaz/Desktop/kedi-cins-tahmini-main
python3 api.py
```

### ✅ Yöntem 3: Kalıcı olarak ayarlayın (macOS/Linux)

```bash
echo 'export GEMINI_API_KEY="BURAYA-KENDI-API-KEY-INIZI-YAZIN"' >> ~/.zshrc
source ~/.zshrc
```

## 3️⃣ Test Etme

API'yi başlattıktan sonra, frontend'de bir kedi fotoğrafı yükleyin. Eğer API key doğruysa:
- ✅ Kedi cinsi bilgileri görünecek
- ✅ Fotoğraf analizi (yaş, sağlık durumu) görünecek

Eğer quota hatası alırsanız:
- ⚠️ API key'inizin günlük limiti dolmuş olabilir
- ⚠️ Yeni bir API key oluşturmayı deneyin
- ⚠️ Veya ertesi gün tekrar deneyin

## 📝 Notlar

- API key'inizi **asla GitHub'a commit etmeyin**
- API key'inizi **güvenli tutun**, başkalarıyla paylaşmayın
- Ücretsiz plan genellikle günde 15 RPM (requests per minute) limiti vardır

## 🔗 Faydalı Linkler

- Google AI Studio: https://aistudio.google.com/
- API Key Sayfası: https://aistudio.google.com/app/apikey
- Fiyatlandırma: https://ai.google.dev/pricing

