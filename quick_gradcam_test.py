#!/usr/bin/env python3
"""
Quick Grad-CAM Test - Basit test ve doğrulama
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import sys
import numpy as np

# Add project to path
sys.path.insert(0, '/Users/barkinto/Desktop/Projeler/kedi-cins-tahmini-main')

from gradcam import GradCAM

def test_gradcam():
    """Grad-CAM'ı test et"""
    print("🔥 Grad-CAM Quick Test")
    print("=" * 60)
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"📱 Device: {device}")
    
    # Model yükle
    print("\n📂 Model yükleniyor...")
    MODEL_PATH = 'runs/resnet50_v2/weights/best.pth'
    
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model bulunamadı: {MODEL_PATH}")
        return False
    
    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
    num_classes = len(checkpoint['class_names'])
    class_names = checkpoint['class_names']
    
    # Model architecture
    model = models.resnet50(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, num_classes)
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    print(f"✅ Model yüklendi ({num_classes} sınıf)")
    
    # Grad-CAM initialize
    print("\n🔥 Grad-CAM initialize ediliyor...")
    try:
        gradcam = GradCAM(model, model.layer4[-1])
        print("✅ Grad-CAM hazır")
    except Exception as e:
        print(f"❌ Grad-CAM hatası: {e}")
        return False
    
    # Dummy image oluştur test için
    print("\n📸 Test görsel oluşturuluyor...")
    dummy_image = Image.new('RGB', (224, 224), color='red')
    
    # Transform
    transform = transforms.Compose([
        transforms.Resize(int(224 * 1.15)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    input_tensor = transform(dummy_image).unsqueeze(0).to(device)
    print("✅ Görsel transform edildi")
    
    # Predict
    print("\n🧠 Tahmin yapılıyor...")
    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.softmax(output, dim=1)
        predicted_class = output.argmax(dim=1).item()
        confidence = probs[0, predicted_class].item() * 100
    
    predicted_breed = class_names[predicted_class]
    print(f"✅ Tahmin: {predicted_breed} ({confidence:.2f}%)")
    
    # Grad-CAM oluştur
    print("\n🔥 Grad-CAM oluşturuluyor...")
    try:
        cam = gradcam.generate_cam(input_tensor, predicted_class, device=device)
        print(f"✅ CAM oluşturuldu (shape: {cam.shape})")
    except Exception as e:
        print(f"❌ CAM hatası: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Overlay
    print("\n📊 Görselleştirme yapılıyor...")
    try:
        overlay = gradcam.overlay_cam_on_image(dummy_image, cam, alpha=0.4)
        print("✅ Overlay oluşturuldu")
    except Exception as e:
        print(f"❌ Overlay hatası: {e}")
        return False
    
    # Kaydet
    output_file = 'gradcam_test_result.png'
    overlay.save(output_file)
    print(f"✅ Sonuç kaydedildi: {output_file}")
    
    print("\n" + "=" * 60)
    print("✅ Grad-CAM Test Başarılı!")
    print("\nNe yaptığınız:")
    print("1. ResNet50 modelini yükledik")
    print("2. Grad-CAM handler'ını initialize ettik")
    print("3. Dummy test görselini tahmin ettik")
    print("4. Grad-CAM ısı haritası oluşturduk")
    print("5. Orijinal görsel üzerine overlay yaptık")
    print("6. Sonucu PNG olarak kaydettik")
    
    return True

if __name__ == '__main__':
    try:
        success = test_gradcam()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
