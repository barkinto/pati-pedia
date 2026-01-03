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

# 🐱 PatiPedia - Kedi Cinsi Tanıma Sistemi

Yapay zeka destekli, 59 farklı kedi cinsini tanıyabilen modern web uygulaması.

## 🌟 Özellikler

- 🎯 **59 Kedi Cinsi**: Abyssinian'dan Tabby'ye kadar geniş yelpaze
- 🧠 **İki Aşamalı AI**: YOLO11 kedi tespiti + ResNet50 cins sınıflandırma
- 🛡️ **Vahşi Kedi Tespiti**: Entropi analizi ile vahşi kedi uyarısı
- 📚 **Irk Ansiklopedisi**: Her cins için detaylı sağlık, beslenme, bakım ve davranış bilgileri
- 🎨 **Modern Arayüz**: PatiPedia tasarımı ile kullanıcı dostu deneyim
- ⚡ **Hızlı Analiz**: CUDA destekli GPU hızlandırma

## 🚀 Kullanım

1. Kedi fotoğrafı yükleyin (drag & drop veya dosya seçimi)
2. "FOTOĞRAF YÜKLE" butonuna tıklayın
3. AI analizi otomatik başlar:
   - YOLO11: Fotoğrafta kedi var mı?
   - ResNet50: Hangi cins?
   - Entropi: Vahşi kedi mi?
4. Sonuçları görüntüleyin:
   - En olası 5 cins tahmini
   - Güven yüzdeleri
   - Irk ansiklopedisi bilgileri

## 🧠 Model Mimarisi

### 1. YOLO11n (Cat Detection)
- **Parameters**: 2.6M
- **Purpose**: Kedi tespiti ve filtreleme
- **Speed**: ~50ms per image

### 2. ResNet50 (Breed Classification)
- **Parameters**: 24.6M
- **Accuracy**: 64.67%
- **Classes**: 59 cat breeds
- **Speed**: ~100ms per image

### 3. Entropi Analizi (Wild Cat Detection)
- **Threshold**: 0.9
- **Purpose**: Vahşi kedi tespit ve uyarı

## 📊 Performans

- **Total Inference**: ~200ms (YOLO 50ms + ResNet50 100ms + overhead)
- **Validation Accuracy**: 64.67%
- **Top-5 Accuracy**: ~85%
- **Dataset**: 110,557 images (88,741 train + 21,816 val)

## 🛠️ Teknolojiler

**Backend:**
- Python 3.11
- PyTorch 2.5.1
- Flask 3.0.0
- Ultralytics YOLO11n

**Frontend:**
- React 19.2.0
- Vite 7.2.4
- Modern CSS (PatiPedia design)

**Infrastructure:**
- Docker
- CUDA 12.1+ (GPU support)
- Hugging Face Spaces

## 📝 Desteklenen Kedi Cinsleri

Abyssinian, American Bobtail, American Curl, American Shorthair, American Wirehair, Applehead Siamese, Balinese, Bengal, Birman, Bombay, British Shorthair, Burmese, Burmilla, Calico, Canadian Hairless, Chartreux, Chausie, Chinchilla, Cornish Rex, Cymric, Devon Rex, Dilute Calico, Dilute Tortoiseshell, Domestic Long Hair, Domestic Medium Hair, Domestic Short Hair, Egyptian Mau, Exotic Shorthair, Extra-Toes Cat, Havana, Himalayan, Japanese Bobtail, Javanese, Korat, LaPerm, Maine Coon, Manx, Munchkin, Nebelung, Norwegian Forest Cat, Ocicat, Oriental Long Hair, Oriental Short Hair, Oriental Tabby, Persian, Pixiebob, Ragamuffin, Ragdoll, Russian Blue, Scottish Fold, Selkirk Rex, Siamese, Siberian, Silver, Singapura, Snowshoe, Somali, Sphynx, Tabby

## 👨‍💻 Geliştirici

**Berke Gazioğlu**
- GitHub: [@berkegazioglu](https://github.com/berkegazioglu)
- Repository: [kedi-cins-tahmini](https://github.com/berkegazioglu/kedi-cins-tahmini)

## 📜 Lisans

MIT License - Açık kaynak projesi

---

**🎉 PatiPedia ile kedinizin cinsini keşfedin!**
