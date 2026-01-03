# 🐱 Kedi Cinsi Tahmin - React Frontend + Flask API

Bu proje, React frontend ve Flask RESTful API kullanarak kedi cinsi tahmin sistemi sunar.

## 🚀 Hızlı Başlangıç

### 1. Backend API'yi Başlatın

```bash
# Terminal 1 - Backend API
cd /Users/aliefeyilmaz/Desktop/kedi-cins-tahmini-main
pip install flask flask-cors
python api.py
```

Backend API `http://localhost:5001` adresinde çalışacak.

### 2. Frontend'i Başlatın

```bash
# Terminal 2 - React Frontend
cd /Users/aliefeyilmaz/Desktop/kedi-cins-frontend
npm run dev
```

Frontend `http://localhost:5173` adresinde çalışacak.

## 📡 API Endpoints

### `GET /api/health`
API sağlık kontrolü
```json
{
  "status": "healthy",
  "model_loaded": true,
  "yolo_loaded": true,
  "device": "cpu",
  "num_classes": 59
}
```

### `POST /api/predict`
Kedi cinsi tahmini yap
- **Body**: `multipart/form-data`
  - `image`: Image file (required)
  - `skip_detection`: "true" or "false" (optional)

**Response:**
```json
{
  "success": true,
  "predictions": [
    {
      "breed": "Persian",
      "confidence": 85.23
    },
    ...
  ],
  "cat_detection": {
    "detected": true,
    "confidence": 92.5,
    "message": "Cat detected (confidence: 0.92)"
  }
}
```

### `GET /api/classes`
Tüm kedi cinslerini listele
```json
{
  "classes": ["Abyssinian", "Persian", ...],
  "total": 59
}
```

## 🎨 Frontend Özellikleri

- ✅ Modern ve responsive tasarım
- ✅ Drag & drop görsel yükleme
- ✅ Gerçek zamanlı tahmin
- ✅ Top-5 tahmin sonuçları
- ✅ Güven yüzdeleri ve görselleştirme
- ✅ YOLO kedi tespiti entegrasyonu
- ✅ Hata yönetimi

## 🛠️ Teknolojiler

**Backend:**
- Flask 3.0.0
- Flask-CORS
- PyTorch
- YOLO11

**Frontend:**
- React 18
- Vite
- Modern CSS

## 📝 Notlar

- Backend API port: `5000`
- Frontend dev server port: `5173`
- CORS aktif (localhost için)
- Model dosyaları `runs/` klasöründe olmalı

