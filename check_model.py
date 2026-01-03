import torch

# Load best model checkpoint
ckpt = torch.load('runs/resnet50/weights/best.pth', weights_only=False)

print("\n" + "="*60)
print("📊 ResNet-50 Model Bilgileri")
print("="*60)
print(f"Epoch: {ckpt.get('epoch', 'N/A') + 1}")
print(f"Val Loss: {ckpt.get('val_loss', 0):.4f}")
print(f"Best Val Loss: {ckpt.get('best_val_loss', 0):.4f}")
print(f"Toplam Sınıf: {len(ckpt.get('class_names', []))}")
print(f"\nModel Yolu: runs/resnet50/weights/best.pth")
print(f"Model Boyutu: {91.3} MB")
print("="*60)

# Show first 10 classes
classes = ckpt.get('class_names', [])
if classes:
    print(f"\nİlk 10 Sınıf:")
    for i, cls in enumerate(classes[:10], 1):
        print(f"  {i}. {cls}")
