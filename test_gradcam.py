#!/usr/bin/env python3
"""
Grad-CAM Test Script
Kedi fotoğrafı ile Grad-CAM görselleştirmesini test eder
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import json
from gradcam import GradCAM, SalienceMap, image_to_base64

# Model parametreleri
MODEL_PATH = 'runs/resnet50_v2/weights/best.pth'
TEST_IMAGE = None  # Test görseli seç

def main():
    print("🚀 Grad-CAM Test Script")
    print("=" * 50)
    
    # Device seç
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"📱 Device: {device}")
    
    # Model yükle
    print("\n📂 Model yükleniyor...")
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model bulunamadı: {MODEL_PATH}")
        return
    
    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
    num_classes = len(checkpoint['class_names'])
    class_names = checkpoint['class_names']
    
    model = models.resnet50(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    print(f"✅ Model yüklendi ({num_classes} sınıf)")
    
    # Grad-CAM initialize et
    print("\n🔥 Grad-CAM initialize ediliyor...")
    gradcam = GradCAM(model, model.layer4[-1])
    print("✅ Grad-CAM hazır")
    
    # Test görseli bul
    test_image_path = None
    if TEST_IMAGE and os.path.exists(TEST_IMAGE):
        test_image_path = TEST_IMAGE
    else:
        # Klasik test görselleri ara
        possible_paths = [
            'test_image.jpg',
            'test.jpg',
            'sample.jpg',
            'cat.jpg'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                test_image_path = path
                break
    
    if not test_image_path:
        print("\n⚠️ Test görseli bulunamadı.")
        print("Lütfen test görseli ekleyin ve TEST_IMAGE değişkenini güncelleyin.")
        print("\nGrad-CAM kullanımı:")
        print("  1. Görseli yükle: image = Image.open('image.jpg')")
        print("  2. Transform et ve predikt et")
        print("  3. Grad-CAM oluştur: cam = gradcam.generate_cam(input_tensor, class_idx)")
        print("  4. Görselleştir: overlay = gradcam.overlay_cam_on_image(image, cam)")
        return
    
    print(f"\n📸 Test görseli: {test_image_path}")
    
    # Görseli işle
    print("\n🔍 Görsel işleniyor...")
    image = Image.open(test_image_path).convert('RGB')
    
    transform = transforms.Compose([
        transforms.Resize(int(224 * 1.15)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    input_tensor = transform(image).unsqueeze(0).to(device)
    
    # Tahmin yap
    print("\n🧠 Tahmin yapılıyor...")
    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.softmax(output, dim=1)
        predicted_class = output.argmax(dim=1).item()
        confidence = probs[0, predicted_class].item() * 100
    
    predicted_breed = class_names[predicted_class]
    print(f"✅ Tahmin: {predicted_breed} (Güven: {confidence:.2f}%)")
    
    # Grad-CAM oluştur
    print("\n🔥 Grad-CAM oluşturuluyor...")
    cam = gradcam.generate_cam(input_tensor, predicted_class, device=device)
    print("✅ Grad-CAM oluşturuldu")
    
    # Görselleştir
    print("\n📊 Görselleştirme yapılıyor...")
    overlay = gradcam.overlay_cam_on_image(image, cam, alpha=0.4)
    
    # Kaydet
    output_path = f'gradcam_result_{predicted_breed.replace(" ", "_")}.png'
    overlay.save(output_path)
    print(f"✅ Sonuç kaydedildi: {output_path}")
    
    # Saliency Map (bonus)
    print("\n🎯 Saliency Map oluşturuluyor...")
    try:
        saliency = SalienceMap()
        saliency_map = saliency.generate(test_image_path, model, device=device)
        print("✅ Saliency Map oluşturuldu")
    except Exception as e:
        print(f"⚠️ Saliency Map hatası: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test tamamlandı!")

if __name__ == '__main__':
    main()
