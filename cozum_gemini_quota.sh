#!/bin/bash
# Gemini API Quota Sorunu Çözüm Scripti

echo "🔧 Gemini API Quota Sorunu Çözüm Rehberi"
echo "=========================================="
echo ""

# Check if API key is provided
if [ -z "$1" ]; then
    echo "❌ API Key bulunamadı!"
    echo ""
    echo "📋 Adım Adım Çözüm:"
    echo ""
    echo "1️⃣  Yeni API Key Alın:"
    echo "   - https://aistudio.google.com/app/apikey adresine gidin"
    echo "   - ÖNEMLİ: Farklı bir Google hesabı kullanın!"
    echo "   - 'Create API Key' butonuna tıklayın"
    echo "   - Key'i kopyalayın"
    echo ""
    echo "2️⃣  Key'i Test Edin:"
    echo "   ./test_gemini_key.sh YOUR_NEW_API_KEY"
    echo ""
    echo "3️⃣  Key'i Projeye Ekleyin:"
    echo "   python3 update_api_key.py YOUR_NEW_API_KEY"
    echo ""
    echo "4️⃣  Projeyi Yeniden Başlatın:"
    echo "   pkill -f 'api.py'"
    echo "   python3 api.py"
    echo ""
    exit 1
fi

NEW_KEY="$1"

echo "🔑 Yeni API Key: ${NEW_KEY:0:20}..."
echo ""

# Step 1: Test the key
echo "1️⃣  API Key test ediliyor..."
./test_gemini_key.sh "$NEW_KEY"
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
    echo ""
    echo "❌ API Key test başarısız!"
    echo "💡 Lütfen yeni bir API key oluşturun veya birkaç saat bekleyin."
    exit 1
fi

echo ""
echo "2️⃣  API Key projeye ekleniyor..."
python3 update_api_key.py "$NEW_KEY"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ API Key başarıyla güncellendi!"
    echo ""
    echo "3️⃣  Projeyi yeniden başlatmak için:"
    echo "   pkill -f 'api.py'"
    echo "   python3 api.py"
    echo ""
    echo "🌐 Web sitesi: http://localhost:5001"
else
    echo ""
    echo "❌ API Key güncellenemedi!"
    echo "💡 Manuel olarak güncelleyin:"
    echo "   - start_api.sh dosyasını düzenleyin"
    echo "   - api.py dosyasında 2 yerde güncelleyin (satır ~360 ve ~490)"
fi

