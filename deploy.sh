#!/bin/bash

# Kedi Cinsi Tanıma - Docker Deployment Script

echo "🐱 Kedi Cinsi Tanıma Sistemi - Docker Deployment"
echo "================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker bulunamadı. Lütfen Docker Desktop'ı kurun:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker bulundu"

# Check if model file exists
if [ ! -f "runs/resnet50/weights/best.pth" ]; then
    echo "❌ Model dosyası bulunamadı!"
    echo "   Lütfen best.pth dosyasını runs/resnet50/weights/ klasörüne koyun"
    exit 1
fi

echo "✅ Model dosyası bulundu"

# Check for GPU support
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU algılandı"
    USE_GPU=true
else
    echo "⚠️  GPU bulunamadı, CPU modu kullanılacak"
    USE_GPU=false
fi

# Build Docker image
echo ""
echo "📦 Docker image oluşturuluyor..."
docker build -t kedi-cins-tahmini:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build başarısız!"
    exit 1
fi

echo "✅ Docker image oluşturuldu"

# Run container
echo ""
echo "🚀 Container başlatılıyor..."

if [ "$USE_GPU" = true ]; then
    docker-compose up -d
else
    docker run -d \
        --name kedi-cins-tahmini \
        -p 8501:8501 \
        -v "$(pwd)/runs/resnet50/weights/best.pth:/app/runs/resnet50/weights/best.pth:ro" \
        kedi-cins-tahmini:latest
fi

if [ $? -ne 0 ]; then
    echo "❌ Container başlatılamadı!"
    exit 1
fi

echo "✅ Container başarıyla başlatıldı"
echo ""
echo "🌐 Web arayüzü: http://localhost:8501"
echo ""
echo "📋 Kullanım:"
echo "   • Durdur: docker stop kedi-cins-tahmini"
echo "   • Başlat: docker start kedi-cins-tahmini"
echo "   • Loglar: docker logs -f kedi-cins-tahmini"
echo "   • Kaldır: docker rm -f kedi-cins-tahmini"
echo ""
