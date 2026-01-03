# Kedi Cinsi Tanıma - Docker Deployment Script (Windows)

Write-Host "`n🐱 Kedi Cinsi Tanıma Sistemi - Docker Deployment" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Gray

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker bulundu" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker bulunamadı. Lütfen Docker Desktop'ı kurun:" -ForegroundColor Red
    Write-Host "   https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if model file exists
if (-Not (Test-Path "runs\resnet50\weights\best.pth")) {
    Write-Host "❌ Model dosyası bulunamadı!" -ForegroundColor Red
    Write-Host "   Lütfen best.pth dosyasını runs\resnet50\weights\ klasörüne koyun" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Model dosyası bulundu" -ForegroundColor Green

# Check for GPU support
try {
    nvidia-smi | Out-Null
    Write-Host "✅ NVIDIA GPU algılandı" -ForegroundColor Green
    $UseGPU = $true
} catch {
    Write-Host "⚠️  GPU bulunamadı, CPU modu kullanılacak" -ForegroundColor Yellow
    $UseGPU = $false
}

# Build Docker image
Write-Host "`n📦 Docker image oluşturuluyor..." -ForegroundColor Cyan
docker build -t kedi-cins-tahmini:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build başarısız!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker image oluşturuldu" -ForegroundColor Green

# Run container
Write-Host "`n🚀 Container başlatılıyor..." -ForegroundColor Cyan

if ($UseGPU) {
    docker-compose up -d
} else {
    docker run -d `
        --name kedi-cins-tahmini `
        -p 8501:8501 `
        -v "${PWD}\runs\resnet50\weights\best.pth:/app/runs/resnet50/weights/best.pth:ro" `
        kedi-cins-tahmini:latest
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Container başlatılamadı!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Container başarıyla başlatıldı" -ForegroundColor Green
Write-Host "`n🌐 Web arayüzü: http://localhost:8501" -ForegroundColor Cyan
Write-Host "`n📋 Kullanım:" -ForegroundColor Yellow
Write-Host "   • Durdur: docker stop kedi-cins-tahmini" -ForegroundColor White
Write-Host "   • Başlat: docker start kedi-cins-tahmini" -ForegroundColor White
Write-Host "   • Loglar: docker logs -f kedi-cins-tahmini" -ForegroundColor White
Write-Host "   • Kaldır: docker rm -f kedi-cins-tahmini" -ForegroundColor White
Write-Host ""
