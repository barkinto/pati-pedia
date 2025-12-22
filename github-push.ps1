# GitHub Push Helper Script
# Projenizi GitHub'a yüklemek için bu scripti kullanın

Write-Host "`n🚀 GITHUB PUSH HELPER" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# Kullanıcıdan GitHub username al
$username = Read-Host "`nGitHub kullanıcı adınız"
$repoName = "kedi-cins-tahmini"

Write-Host "`n📋 Repository bilgileri:" -ForegroundColor Yellow
Write-Host "   Kullanıcı: $username" -ForegroundColor White
Write-Host "   Repo: $repoName" -ForegroundColor White
Write-Host "   URL: https://github.com/$username/$repoName" -ForegroundColor Cyan

$confirm = Read-Host "`n✅ Devam edilsin mi? (E/H)"

if ($confirm -ne "E" -and $confirm -ne "e") {
    Write-Host "`n❌ İptal edildi" -ForegroundColor Red
    exit
}

Write-Host "`n🔗 Remote ekleniyor..." -ForegroundColor Cyan
git remote remove origin 2>$null
git remote add origin "https://github.com/$username/$repoName.git"

Write-Host "📤 Branch main'e çevriliyor..." -ForegroundColor Cyan
git branch -M main

Write-Host "🚀 GitHub'a push ediliyor..." -ForegroundColor Yellow
Write-Host "(Bu işlem birkaç dakika sürebilir - ~100 MB veri)`n" -ForegroundColor Gray

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ BAŞARILI! Proje GitHub'a yüklendi!" -ForegroundColor Green
    Write-Host "`n🌐 Repository linki:" -ForegroundColor Cyan
    Write-Host "   https://github.com/$username/$repoName" -ForegroundColor White
    Write-Host "`n📋 Arkadaşlarınız için kurulum:" -ForegroundColor Yellow
    Write-Host "   git clone https://github.com/$username/$repoName.git" -ForegroundColor Gray
    Write-Host "   cd $repoName" -ForegroundColor Gray
    Write-Host "   .\deploy.ps1" -ForegroundColor Gray
} else {
    Write-Host "`n❌ Hata oluştu!" -ForegroundColor Red
    Write-Host "Muhtemel nedenler:" -ForegroundColor Yellow
    Write-Host "  1. GitHub'da repository oluşturmadınız" -ForegroundColor White
    Write-Host "  2. Yanlış kullanıcı adı" -ForegroundColor White
    Write-Host "  3. GitHub authentication gerekli" -ForegroundColor White
    Write-Host "`nÇözüm: GitHub'da yeni repository oluşturun:" -ForegroundColor Cyan
    Write-Host "  https://github.com/new" -ForegroundColor White
}

Write-Host ""
