"""
show_classes.py - Model sınıflarını göster
"""
import torch

checkpoint = torch.load('runs/resnet50/weights/best.pth', weights_only=False)
classes = checkpoint['class_names']

print(f'\n{"="*60}')
print(f'📊 MODEL SINIF İSİMLERİ')
print(f'{"="*60}')
print(f'\nToplam sınıf sayısı: {len(classes)}\n')

for i, name in enumerate(classes):
    print(f'{i:2d}. {name}')

print(f'\n{"="*60}')
print(f'\n💡 Bu isimler şuradan geliyor:')
print(f'   • Dataset: images_split/train/ klasörü')
print(f'   • Her klasör adı = bir sınıf ismi')
print(f'   • Model bu isimleri eğitim sırasında öğrendi')
print(f'\n{"="*60}\n')
