#!/bin/bash

echo "🐱 PatiPedia - Gemini AI Kurulum Sihirbazı"
echo "--------------------------------------------"
echo "Bu proje, görsel analiz (kedi yaşı, sağlık durumu vb.) için Google Gemini AI kullanır."
echo "Gemini API şu anda ücretsizdir."
echo ""
echo "1. https://aistudio.google.com/app/apikey adresine gidin."
echo "2. Google hesabınızla giriş yapın."
echo "3. 'Create API key' butonuna tıklayın."
echo "4. Oluşturulan anahtarı kopyalayın."
echo ""
read -p "Lütfen API Anahtarınızı (API Key) yapıştırın: " api_key

if [ -z "$api_key" ]; then
    echo "❌ API anahtarı boş olamaz!"
    exit 1
fi

# .env dosyası oluştur veya güncelle
if [ -f .env ]; then
    # Varsa yedeğini al
    cp .env .env.bak
    # Varsa eski key'i sil
    grep -v "GEMINI_API_KEY" .env > .env.tmp
    mv .env.tmp .env
fi

echo "GEMINI_API_KEY=$api_key" >> .env

echo ""
echo "✅ API Anahtarı .env dosyasına kaydedildi!"
echo "Şimdi uygulamayı yeniden başlatmanız gerekiyor."
echo ""
read -p "Uygulamayı şimdi yeniden başlatmak ister misiniz? (e/h): " restart

if [ "$restart" = "e" ] || [ "$restart" = "E" ]; then
    echo "🔄 Uygulama yeniden başlatılıyor..."
    # Kill existing python process if running (simple check)
    pkill -f "python app.py"
    ./start.sh
else
    echo "ℹ️ Değişikliklerin aktif olması için './start.sh' ile uygulamayı yeniden başlatın."
fi
