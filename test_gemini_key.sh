#!/bin/bash
# Test Gemini API Key

echo "🔑 Gemini API Key Test Scripti"
echo "================================"
echo ""

# Get API key from user or use environment variable
if [ -z "$1" ]; then
    if [ -z "$GEMINI_API_KEY" ]; then
        echo "❌ API Key bulunamadı!"
        echo ""
        echo "Kullanım:"
        echo "  ./test_gemini_key.sh YOUR_API_KEY"
        echo "  veya"
        echo "  export GEMINI_API_KEY='YOUR_API_KEY'"
        echo "  ./test_gemini_key.sh"
        exit 1
    else
        API_KEY="$GEMINI_API_KEY"
        echo "✅ Environment variable'dan API key alındı"
    fi
else
    API_KEY="$1"
    echo "✅ Komut satırından API key alındı"
fi

echo ""
echo "🧪 API Key test ediliyor..."
echo ""

# Test API call
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" \
  -H 'Content-Type: application/json' \
  -H "X-goog-api-key: $API_KEY" \
  -X POST \
  -d '{
    "contents": [{
      "parts": [{
        "text": "Merhaba, bu bir test mesajıdır. Lütfen sadece \"Test başarılı\" yazın."
      }]
    }]
  }')

# Extract HTTP code
HTTP_CODE=$(echo "$RESPONSE" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

echo "📊 HTTP Status Code: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API Key ÇALIŞIYOR!"
    echo ""
    echo "📝 Response:"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    echo ""
    echo "🎉 Bu API key'i kullanabilirsiniz!"
elif [ "$HTTP_CODE" = "429" ]; then
    echo "❌ QUOTA AŞILMIŞ!"
    echo ""
    echo "⚠️  Bu API key'in quota limiti aşılmış."
    echo "💡 Çözüm:"
    echo "   1. Farklı bir Google hesabı ile yeni key oluşturun"
    echo "   2. Birkaç saat bekleyin (quota reset olması için)"
    echo "   3. Google Cloud Console'da quota durumunu kontrol edin"
elif [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "❌ API KEY GEÇERSİZ!"
    echo ""
    echo "⚠️  Bu API key geçersiz veya süresi dolmuş."
    echo "💡 Çözüm:"
    echo "   1. Google AI Studio'da yeni bir key oluşturun"
    echo "   2. Key'i doğru kopyaladığınızdan emin olun"
else
    echo "❌ HATA: HTTP $HTTP_CODE"
    echo ""
    echo "📝 Response:"
    echo "$BODY" | head -20
fi

echo ""
echo "================================"

