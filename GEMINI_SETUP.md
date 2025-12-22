# 🤖 Gemini AI Entegrasyonu

Bu proje, Google Gemini AI kullanarak tahmin edilen kedi cinsinin detaylı bilgilerini sunar.

## 🔑 Gemini API Key Alma

1. **Google AI Studio'ya gidin:**
   - https://makersuite.google.com/app/apikey
   - veya https://aistudio.google.com/app/apikey

2. **Google hesabınızla giriş yapın**

3. **"Create API Key" butonuna tıklayın**

4. **API Key'inizi kopyalayın**

## ⚙️ API Key'i Ayarlama

### Yöntem 1: start_api.sh scriptini kullanın (Önerilen)
```bash
# start_api.sh dosyasını düzenleyin ve API key'inizi ekleyin
# Sonra:
./start_api.sh
```

### Yöntem 2: Terminal'de geçici olarak (Sadece o terminal için)
**macOS/Linux:**
```bash
export GEMINI_API_KEY="your-api-key-here"
python3 api.py
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
python api.py
```

### Yöntem 3: Kalıcı olarak ayarlamak için

**macOS/Linux (.zshrc veya .bashrc):**
```bash
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
- Sistem özellikleri → Ortam değişkenleri → Yeni ekle
- Değişken adı: `GEMINI_API_KEY`
- Değişken değeri: API key'iniz

## 🚀 Kullanım

API key'i ayarladıktan sonra, backend API'yi başlatın:

```bash
cd /Users/aliefeyilmaz/Desktop/kedi-cins-tahmini-main
python3 api.py
```

Frontend'de bir kedi fotoğrafı yükleyip tahmin yaptığınızda, en üstteki tahmin için otomatik olarak Gemini AI'dan kedi cinsi hakkında detaylı bilgi gelecektir.

## 📡 API Endpoint

**POST /api/breed-info**

Request:
```json
{
  "breed": "Persian"
}
```

Response:
```json
{
  "success": true,
  "breed": "Persian",
  "info": "Persian kedisi hakkında detaylı bilgi..."
}
```

## ⚠️ Notlar

- Gemini API ücretsiz kullanım limiti vardır
- API key'i güvenli tutun, GitHub'a commit etmeyin
- `.env` dosyası kullanarak da yönetebilirsiniz (python-dotenv paketi ile)

