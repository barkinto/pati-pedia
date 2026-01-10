# 🔥 Grad-CAM - Açıklanabilir Yapay Zeka (XAI) Modülü

## Nedir?

**Grad-CAM (Gradient-weighted Class Activation Mapping)**, derin öğrenme modellerinin kararlarını görselleştiren bir tekniktir. Model, bir kedinin cinsini belirlerken görselin **hangi bölgelerine odaklandığını** gösteren ısı haritası oluşturur.

## Özellikler

✅ **Model İçinlik**: Modelin neden belirli bir kedi cinsi tahmini yaptığını gösterir
✅ **Ölçeklenebilir**: ResNet50 ile fully compatible
✅ **Hızlı**: Backward pass ile minimal overhead
✅ **Görselleştirme**: Base64 encoded PNG ile HTTP cevaplarında gönderilebilir

## Kullanım

### 1. API Endpoint (Flask)

```bash
POST /api/gradcam
Content-Type: multipart/form-data

# Request:
- image: [binary] Kedi fotoğrafı

# Response:
{
  "success": true,
  "predicted_class": "British Shorthair",
  "confidence": 85.23,
  "gradcam_image": "data:image/png;base64,...",
  "explanation": "🔥 Grad-CAM Görselleştirmesi: Kırmızı bölgeler..."
}
```

### 2. Streamlit App (app_resnet50.py)

Tahmin sonuçlarında otomatik olarak Grad-CAM görselleştirmesi gösterilir:
- Orijinal görsel ve Grad-CAM overlay yan yana gösterilir
- Kırmızı bölgeler = yüksek aktivasyon (önemli özellikler)
- Mavi bölgeler = düşük aktivasyon

### 3. Python Script

```python
from gradcam import GradCAM
import torch

# Grad-CAM handler'ı initialize et
gradcam = GradCAM(model, model.layer4[-1])

# Görsel işle
input_tensor = transform(image).unsqueeze(0).to(device)

# CAM hesapla
cam = gradcam.generate_cam(input_tensor, class_idx, device=device)

# Görselleştir
overlay = gradcam.overlay_cam_on_image(image, cam, alpha=0.4)
overlay.save('gradcam_result.png')
```

## Dosyalar

- **gradcam.py**: Grad-CAM ve Saliency Map implementasyonu
- **test_gradcam.py**: Standalone test script'i
- **app_resnet50.py**: Streamlit app'a entegre Grad-CAM gösterimi
- **api.py**: Flask API endpoint'i

## Teknik Detaylar

### Grad-CAM Algoritması

1. **Forward Pass**: Görsel modelde işlenir, aktivasyonlar kaydedilir
2. **Backward Pass**: Target sınıf için gradientler hesaplanır
3. **CAM Hesaplama**: `CAM = Σ(weight_k * activation_k)`
4. **ReLU Uygulama**: Sadece pozitif etkiler gösterilir
5. **Normalizasyon**: Değerler 0-1 aralığına normalize edilir

### Entegrasyonlar

- **ResNet50 Layer4**: Son residual blok kullanılır (yüksek-seviye özellikler)
- **OpenCV**: Isı haritası oluşturmak için (COLORMAP_JET)
- **PyTorch**: Gradient hesaplamaları

## Örnek Çıktı

```
Tahmin: British Shorthair (85% güven)

[Orijinal Görsel]        [Grad-CAM Overlay]
    🐱                        🔥🔥🔥
   [kulaklara kırmızı]      [yüzde kırmızı]
    
Açıklama: Model, kedinin kulaklarına ve yüzüne bakarak
British Shorthair tanısını yaptı.
```

## Referanslar

- **Paper**: [Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization](https://arxiv.org/abs/1610.02055)
- **Authors**: Selvaraju, Das, Vedantam, Parikh, Batra (2017)

## Geliştirilecek

- [ ] Saliency Maps tam entegrasyonu
- [ ] Attention mechanisms visualization
- [ ] İntegrasyon test görselleri ile
- [ ] Batch processing destekleme
- [ ] GPU optimization (backward hook caching)
