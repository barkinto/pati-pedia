# 🚀 Render.com Deployment Guide

Bu proje Render.com üzerinde ücretsiz olarak deploy edilebilir.

## 📋 Gereksinimler

- GitHub hesabı
- Render.com hesabı (ücretsiz)
- Git LFS (model dosyaları için)

## 🔧 Deployment Adımları

### 1. Model Dosyalarını Hazırlayın

Model dosyaları Git LFS ile yönetilmektedir. Render.com deployment sırasında otomatik olarak indirilecektir.

**Gerekli model dosyaları:**
- `yolo11n.pt` (5.3 MB) - ✅ Repoda mevcut
- `runs/resnet50_v2/weights/best.pth` (270 MB) - ✅ Git LFS
- `cat_breed_info.json` (4 categories × 59 breeds) - ✅ Repoda mevcut

### 2. Render.com'a Deploy

#### 2.1. Render.com Hesabı Oluşturun
1. [render.com](https://render.com) adresine gidin
2. GitHub ile giriş yapın
3. GitHub repository'nizi Render'a bağlayın

#### 2.2. Backend (Flask API) Deploy
1. Dashboard'da **"New +"** → **"Web Service"** seçin
2. GitHub repository'nizi seçin: `berkegazioglu/kedi-cins-tahmini`
3. Yapılandırma:
   - **Name:** `patipedia-api`
   - **Environment:** `Docker`
   - **Region:** `Frankfurt (EU Central)`
   - **Branch:** `main`
   - **Plan:** `Free`
   - **Docker Command:** (Otomatik: `python api.py`)
   - **Health Check Path:** `/api/health`

4. Environment Variables ekleyin:
   ```
   PYTHONUNBUFFERED=1
   PORT=5001
   ```

5. **"Create Web Service"** butonuna tıklayın

⏱️ **İlk build ~10-15 dakika sürecektir** (PyTorch ve model indirmesi)

#### 2.3. Frontend (React) Deploy
1. Dashboard'da **"New +"** → **"Static Site"** seçin
2. Aynı repository'yi seçin
3. Yapılandırma:
   - **Name:** `patipedia-frontend`
   - **Branch:** `main`
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`
   - **Plan:** `Free`

4. Environment Variable ekleyin:
   ```
   VITE_API_URL=https://patipedia-api.onrender.com/api
   ```
   ⚠️ **Not:** Backend deploy edildikten sonra gerçek API URL'ini buraya yazın

5. **"Create Static Site"** butonuna tıklayın

### 3. API URL Güncelleme

Backend deploy tamamlandıktan sonra:

1. Backend URL'ini kopyalayın (örn: `https://patipedia-api.onrender.com`)
2. Frontend'in environment variable'ına ekleyin:
   - Frontend dashboard → **Environment** → **Add Environment Variable**
   - Key: `VITE_API_URL`
   - Value: `https://patipedia-api.onrender.com/api`
3. **"Manual Deploy"** → **"Clear build cache & deploy"** yapın

### 4. CORS Ayarları (Opsiyonel)

`api.py` dosyasında CORS zaten yapılandırılmış:

```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

Production'da güvenlik için frontend domain'ini ekleyin:
```python
CORS(app, resources={r"/api/*": {
    "origins": ["https://patipedia-frontend.onrender.com"]
}})
```

## 📊 Performans Notları

### Ücretsiz Plan Sınırlamaları
- ⏱️ **Cold Start:** İlk istekte ~30-60 saniye boot süresi
- 💤 **Sleep:** 15 dakika inaktiflikten sonra uyku moduna girer
- 🔄 **Monthly Hours:** 750 saat/ay (31 gün × 24 saat = 744 saat)
- 🖥️ **Resources:** 512 MB RAM, CPU-only (GPU yok)

### Model Boyutları
- **Backend Docker Image:** ~3.5 GB (PyTorch + CUDA base)
- **ResNet50 Model:** 270 MB
- **YOLO11n Model:** 5.3 MB
- **Frontend Build:** ~2 MB

### Performans İyileştirmeleri
1. **Keep-Alive Cron Job:** UptimeRobot ile her 14 dakikada ping atın
2. **Model Caching:** İlk boot'tan sonra modeller bellekte kalır
3. **Frontend Caching:** Static assets CDN'den serve edilir

## 🔗 Deployment URL'leri

Deploy tamamlandığında:
- **Frontend:** `https://patipedia-frontend.onrender.com`
- **Backend API:** `https://patipedia-api.onrender.com/api`
- **Health Check:** `https://patipedia-api.onrender.com/api/health`

## 🐛 Sorun Giderme

### Build Hataları

**Git LFS Hatası:**
```bash
# Render'da Git LFS otomatik çalışır, ancak sorun olursa:
git lfs install
git lfs pull
```

**PyTorch CUDA Hatası:**
Render.com ücretsiz planında GPU yok. `api.py` otomatik olarak CPU kullanır:
```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

**Model Bulunamadı Hatası:**
Dockerfile'da model dosyalarının kopyalandığından emin olun:
```dockerfile
COPY runs/resnet50_v2/weights/best.pth runs/resnet50_v2/weights/
COPY yolo11n.pt .
COPY cat_breed_info.json .
```

### Runtime Hataları

**CORS Hatası:**
Backend loglarını kontrol edin:
```bash
# Render dashboard → Logs
```

**Slow Response:**
İlk istek cold start nedeniyle yavaş olabilir. Sonraki istekler hızlı olacaktır.

**Out of Memory:**
Ücretsik plan 512 MB RAM'e sahip. Batch size'ı azaltın:
```python
# api.py içinde
BATCH_SIZE = 1  # Production için
```

## 📈 Monitoring

### Health Check Endpoint
```bash
curl https://patipedia-api.onrender.com/api/health
```

Response:
```json
{
  "status": "healthy",
  "yolo_loaded": true,
  "model_loaded": true,
  "device": "cpu",
  "timestamp": "2025-12-18T12:00:00"
}
```

### UptimeRobot Kurulumu
1. [uptimerobot.com](https://uptimerobot.com) (ücretsiz)
2. **Add New Monitor**:
   - Type: HTTP(s)
   - URL: `https://patipedia-api.onrender.com/api/health`
   - Interval: 14 minutes (cold start önleme)

## 🔒 Güvenlik

### Production Checklist
- [ ] CORS domain restriction ekle
- [ ] Rate limiting (Flask-Limiter)
- [ ] API key authentication (opsiyonel)
- [ ] HTTPS enforce (Render otomatik)
- [ ] Environment variables gizli tut

### Rate Limiting Örneği
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per day", "20 per hour"]
)

@app.route('/api/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict():
    # ...
```

## 💰 Maliyet

**Ücretsiz Plan:**
- Backend Web Service: $0/month (750 saat)
- Frontend Static Site: $0/month (100 GB bandwidth)
- **Toplam: $0/month** 🎉

**Paid Plan (opsiyonel):**
- Starter: $7/month (no sleep, 512 MB RAM)
- Standard: $25/month (2 GB RAM)
- Pro: $85/month (4 GB RAM + GPU)

## 📚 Kaynaklar

- [Render Docs](https://render.com/docs)
- [Docker Deployment](https://render.com/docs/docker)
- [Static Sites](https://render.com/docs/static-sites)
- [Environment Variables](https://render.com/docs/environment-variables)

---

## ✅ Deployment Checklist

- [ ] GitHub'a kod push edildi
- [ ] Git LFS model dosyaları hazır
- [ ] Render.com hesabı oluşturuldu
- [ ] Backend service deploy edildi
- [ ] Frontend static site deploy edildi
- [ ] API URL frontend'e eklendi
- [ ] CORS ayarları yapılandırıldı
- [ ] Health check endpoint test edildi
- [ ] UptimeRobot monitoring kuruldu (opsiyonel)
- [ ] README.md güncellendi

---

**🎉 Deploy tamamlandığında arkadaşlarınızla paylaşabilirsiniz!**

Frontend URL: `https://patipedia-frontend.onrender.com`
