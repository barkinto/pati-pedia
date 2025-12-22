# 🚀 Hugging Face Spaces Deployment Rehberi

Bu rehber PatiPedia projesini Hugging Face Spaces'e deploy etmek için hazırlanmıştır.

## 📋 Neden Hugging Face Spaces?

- ✅ **Tamamen Ücretsiz** (CPU unlimited)
- ✅ **Git LFS Limiti Yok** (büyük model dosyaları sorun değil)
- ✅ **ML Projeleri için Optimize**
- ✅ **Docker Desteği**
- ✅ **Kolay Deployment** (GitHub'dan otomatik senkronizasyon)
- ✅ **GPU Seçeneği** (opsiyonel, ücretli)

## 🔧 Deployment Adımları

### 1. Hugging Face Hesabı Oluşturun

1. [huggingface.co](https://huggingface.co) adresine gidin
2. **Sign Up** ile ücretsiz hesap oluşturun
3. Email adresinizi doğrulayın

### 2. Yeni Space Oluşturun

1. Profil sayfanızda **"New Space"** butonuna tıklayın
2. Space yapılandırması:
   - **Owner:** Sizin kullanıcı adınız
   - **Space name:** `patipedia` (veya dilediğiniz isim)
   - **License:** MIT
   - **Select the Space SDK:** **Docker**
   - **Space hardware:** **CPU basic** (ücretsiz) - başlangıç için yeterli
   - **Visibility:** **Public** (veya Private)

3. **"Create Space"** butonuna tıklayın

### 3. GitHub Repository'yi Bağlayın

#### Seçenek A: Direkt Git Push (Önerilen)

1. Space oluşturulduktan sonra size bir Git URL verilecek:
   ```
   https://huggingface.co/spaces/[kullanıcı-adınız]/patipedia
   ```

2. Local repository'nize HF remote ekleyin:
   ```bash
   cd C:\Users\berke\OneDrive\Masaüstü\project\kedi-cins-tahmini
   git remote add hf https://huggingface.co/spaces/[kullanıcı-adınız]/patipedia
   ```

3. Gerekli dosyaları push edin:
   ```bash
   # README_SPACES.md'yi README.md olarak kopyalayın
   Copy-Item README_SPACES.md README.md -Force
   
   # Git add & commit
   git add .
   git commit -m "feat: deploy to Hugging Face Spaces"
   
   # HF Spaces'e push
   git push hf main
   ```

#### Seçenek B: GitHub'dan Import

1. Space settings'den **"Files and versions"** sekmesine gidin
2. **"Import repository from GitHub"** seçeneğini kullanın
3. GitHub repository URL'inizi girin: `https://github.com/berkegazioglu/kedi-cins-tahmini`

### 4. README.md'yi Güncelleyin

Hugging Face Spaces, README.md dosyasının başındaki YAML front matter'ı okur:

```yaml
---
title: PatiPedia - Kedi Cinsi Tanıma
emoji: 🐱
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
license: mit
app_port: 7860
---
```

Bu ayarlar zaten `README_SPACES.md` dosyasında mevcut. Deployment öncesi kopyalayın:

```powershell
Copy-Item README_SPACES.md README.md -Force
git add README.md
git commit -m "update: README for HF Spaces"
git push hf main
```

### 5. Build Sürecini İzleyin

1. Space sayfanıza gidin: `https://huggingface.co/spaces/[kullanıcı-adınız]/patipedia`
2. **"Building"** durumunu göreceksiniz
3. **"Logs"** sekmesinden build sürecini takip edebilirsiniz

⏱️ **İlk build ~10-15 dakika sürecektir** (Docker image build + model indirme)

### 6. Space'i Test Edin

Build tamamlandığında:

1. **"App"** sekmesine gidin
2. Kedi fotoğrafı yükleyip test edin
3. API endpoint'leri test edin:
   - Health: `https://[kullanıcı-adınız]-patipedia.hf.space/health`
   - API: `https://[kullanıcı-adınız]-patipedia.hf.space/api/predict`

## 🎯 Dosya Yapısı (Hugging Face Spaces İçin)

```
kedi-cins-tahmini/
├── README.md                      # HF Spaces metadata (YAML front matter)
├── Dockerfile                     # Docker image tanımı
├── requirements.txt               # Python dependencies
├── app.py                         # Ana uygulama (Flask + React serve)
├── api.py                         # Flask API backend
├── cat_breed_info.py             # Irk ansiklopedisi
├── cat_breed_info.json           # Irk bilgileri (JSON)
├── yolo11n.pt                    # YOLO model (Git LFS)
├── runs/resnet50_v2/weights/
│   └── best.pth                  # ResNet50 model (Git LFS)
└── frontend/
    └── dist/                     # React build (production)
        ├── index.html
        ├── assets/
        └── ...
```

## 🔒 Environment Variables (Opsiyonel)

Eğer API key veya gizli değişkenler kullanıyorsanız:

1. Space settings → **"Repository secrets"**
2. **"New secret"** butonuna tıklayın
3. Key-value pair ekleyin

```python
# app.py içinde kullanım
import os
api_key = os.environ.get('API_KEY', 'default_value')
```

## 🚀 GPU Kullanımı (Opsiyonel)

Daha hızlı inference için GPU:

1. Space settings → **"Space hardware"**
2. **"Change hardware"** seçeneğini kullanın
3. GPU seçeneklerinden birini seçin:
   - **T4 small**: $0.60/saat (~$18/ay sürekli çalışırsa)
   - **T4 medium**: $1.00/saat
   - **A10G small**: $3.15/saat

⚠️ **Not**: GPU ücretsiz değil, kullandığınız süre kadar ödeme yaparsınız.

## 📊 Monitoring

### Space Stats
- **"Analytics"** sekmesinden kullanım istatistiklerini görebilirsiniz
- **"Logs"** sekmesinden runtime logları kontrol edebilirsiniz

### Health Check
```bash
curl https://[kullanıcı-adınız]-patipedia.hf.space/health
```

Response:
```json
{
  "status": "healthy",
  "yolo_loaded": true,
  "model_loaded": true,
  "device": "cuda",
  "classes": 59
}
```

## 🐛 Sorun Giderme

### Build Hatası: Git LFS

Eğer model dosyaları indirilmiyorsa:

```bash
# Local'de LFS pull
git lfs pull

# HF remote'a push
git push hf main --force
```

### Port Hatası

Hugging Face Spaces **port 7860** kullanır. `app.py` dosyasında:

```python
port = int(os.environ.get('PORT', 7860))
app.run(host='0.0.0.0', port=port)
```

### Memory Hatası

Ücretsiz plan **16 GB RAM** sağlar. Eğer yetersiz geliyorsa:

1. Batch size'ı azaltın
2. Model caching optimize edin
3. Veya GPU plan'e upgrade edin

### Slow Response

İlk istek cold start nedeniyle yavaş olabilir (~30 saniye). Sonraki istekler hızlı olacaktır.

**Keep-Alive:** UptimeRobot ile ping atarak space'i aktif tutabilirsiniz:
```
https://[kullanıcı-adınız]-patipedia.hf.space/health
```

## 🔄 Güncelleme

Kod değişikliklerini deploy etmek için:

```bash
git add .
git commit -m "update: [değişiklik açıklaması]"
git push hf main
```

Space otomatik olarak rebuild edilecek ve yeni versiyon yayınlanacak.

## 🌐 Custom Domain (Opsiyonel)

Hugging Face Pro plan ($9/ay) ile custom domain:

1. Space settings → **"Custom domain"**
2. Domain adınızı girin (örn: `patipedia.com`)
3. DNS ayarlarını yapılandırın

## 📚 Kaynaklar

- [HF Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Docker SDK](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [Git LFS Guide](https://huggingface.co/docs/hub/repositories-getting-started#git-lfs)

---

## ✅ Deployment Checklist

- [ ] Hugging Face hesabı oluşturuldu
- [ ] Yeni Space oluşturuldu (Docker SDK)
- [ ] README.md YAML front matter eklendi
- [ ] Frontend build yapıldı (`npm run build`)
- [ ] Git remote eklendi (`git remote add hf`)
- [ ] Model dosyaları Git LFS ile push edildi
- [ ] HF Spaces'e push yapıldı (`git push hf main`)
- [ ] Build tamamlandı (~10-15 dakika)
- [ ] Health check test edildi
- [ ] Kedi fotoğrafı ile test edildi
- [ ] Public link paylaşıldı

---

**🎉 Deployment tamamlandığında Space URL'inizi paylaşabilirsiniz!**

Örnek: `https://berkegazioglu-patipedia.hf.space`
