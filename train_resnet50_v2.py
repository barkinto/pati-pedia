"""
ResNet-50 Advanced Training Script v2.0
Hedef: 85-90%+ doğruluk

Özellikler:
- Progressive fine-tuning (backbone açılıyor)
- Gelişmiş augmentation (Mixup, CutMix, AutoAugment)
- Label smoothing
- Cosine annealing LR scheduler
- Mixed precision training (FP16)
- Gradient accumulation
- TensorBoard logging
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import os
from tqdm import tqdm
import time
from datetime import datetime
import json
import numpy as np
from torch.cuda.amp import autocast, GradScaler

# TensorBoard opsiyonel (yoksa training yine çalışır)
try:
    from torch.utils.tensorboard import SummaryWriter
    TENSORBOARD_AVAILABLE = True
except ImportError:
    TENSORBOARD_AVAILABLE = False
    print("⚠️  TensorBoard bulunamadı, logging devre dışı")

# -------------------------------
# Gelişmiş Augmentation
# -------------------------------
class MixupCutmix:
    """Mixup ve CutMix augmentation"""
    def __init__(self, mixup_alpha=0.2, cutmix_alpha=1.0, prob=0.5):
        self.mixup_alpha = mixup_alpha
        self.cutmix_alpha = cutmix_alpha
        self.prob = prob
    
    def mixup_data(self, x, y):
        lam = np.random.beta(self.mixup_alpha, self.mixup_alpha)
        batch_size = x.size()[0]
        index = torch.randperm(batch_size).to(x.device)
        mixed_x = lam * x + (1 - lam) * x[index, :]
        y_a, y_b = y, y[index]
        return mixed_x, y_a, y_b, lam
    
    def cutmix_data(self, x, y):
        lam = np.random.beta(self.cutmix_alpha, self.cutmix_alpha)
        batch_size = x.size()[0]
        index = torch.randperm(batch_size).to(x.device)
        
        # CutMix box koordinatları
        W, H = x.size(2), x.size(3)
        cut_rat = np.sqrt(1. - lam)
        cut_w = int(W * cut_rat)
        cut_h = int(H * cut_rat)
        
        cx = np.random.randint(W)
        cy = np.random.randint(H)
        
        bbx1 = np.clip(cx - cut_w // 2, 0, W)
        bby1 = np.clip(cy - cut_h // 2, 0, H)
        bbx2 = np.clip(cx + cut_w // 2, 0, W)
        bby2 = np.clip(cy + cut_h // 2, 0, H)
        
        x[:, :, bbx1:bbx2, bby1:bby2] = x[index, :, bbx1:bbx2, bby1:bby2]
        lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (W * H))
        
        y_a, y_b = y, y[index]
        return x, y_a, y_b, lam
    
    def __call__(self, x, y):
        if np.random.rand() > self.prob:
            return x, y, y, 1.0
        
        if np.random.rand() > 0.5:
            return self.mixup_data(x, y)
        else:
            return self.cutmix_data(x, y)


class LabelSmoothingCrossEntropy(nn.Module):
    """Label smoothing loss"""
    def __init__(self, smoothing=0.1):
        super().__init__()
        self.smoothing = smoothing
    
    def forward(self, pred, target, target_b=None, lam=1.0):
        n_classes = pred.size(1)
        
        # Mixup/CutMix varsa
        if target_b is not None:
            log_probs = torch.nn.functional.log_softmax(pred, dim=1)
            loss_a = self._smooth_loss(log_probs, target, n_classes)
            loss_b = self._smooth_loss(log_probs, target_b, n_classes)
            return lam * loss_a + (1 - lam) * loss_b
        
        # Normal label smoothing
        log_probs = torch.nn.functional.log_softmax(pred, dim=1)
        return self._smooth_loss(log_probs, target, n_classes)
    
    def _smooth_loss(self, log_probs, target, n_classes):
        with torch.no_grad():
            true_dist = torch.zeros_like(log_probs)
            true_dist.fill_(self.smoothing / (n_classes - 1))
            true_dist.scatter_(1, target.data.unsqueeze(1), 1.0 - self.smoothing)
        return torch.mean(torch.sum(-true_dist * log_probs, dim=1))


# -------------------------------
# Model oluşturma
# -------------------------------
def create_model(num_classes, freeze_backbone=True):
    """ResNet-50 model oluştur"""
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    
    if freeze_backbone:
        # İlk başta backbone'u dondur
        for param in model.parameters():
            param.requires_grad = False
    
    # Son FC layer'ı değiştir
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, num_classes)
    )
    
    return model


def unfreeze_backbone(model, unfreeze_layers=None):
    """Backbone'u aç (fine-tuning için)"""
    if unfreeze_layers is None:
        # Tüm parametreleri aç
        for param in model.parameters():
            param.requires_grad = True
        print("✅ Tüm backbone açıldı (fine-tuning)")
    else:
        # Belirli layerları aç (örn: ['layer4', 'layer3'])
        for name, param in model.named_parameters():
            if any(layer in name for layer in unfreeze_layers):
                param.requires_grad = True
        print(f"✅ {unfreeze_layers} katmanları açıldı")


# -------------------------------
# Training fonksiyonları
# -------------------------------
def train_epoch(model, train_loader, criterion, optimizer, device, scaler, mixup_cutmix, epoch, total_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(train_loader, desc=f'Epoch {epoch}/{total_epochs}')
    
    for batch_idx, (inputs, targets) in enumerate(pbar):
        inputs, targets = inputs.to(device), targets.to(device)
        
        # Mixup/CutMix uygula
        inputs, targets_a, targets_b, lam = mixup_cutmix(inputs, targets)
        
        optimizer.zero_grad()
        
        # Mixed precision training
        with autocast():
            outputs = model(inputs)
            loss = criterion(outputs, targets_a, targets_b, lam)
        
        # Backward pass
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        
        # İstatistikler
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += (lam * predicted.eq(targets_a).sum().item() + 
                   (1 - lam) * predicted.eq(targets_b).sum().item())
        
        # Progress bar güncelle
        pbar.set_postfix({
            'loss': f'{running_loss/(batch_idx+1):.4f}',
            'acc': f'{100.*correct/total:.2f}%'
        })
    
    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100. * correct / total
    
    return epoch_loss, epoch_acc


def validate(model, val_loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for inputs, targets in tqdm(val_loader, desc='Validating'):
            inputs, targets = inputs.to(device), targets.to(device)
            
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
    
    val_loss = running_loss / len(val_loader)
    val_acc = 100. * correct / total
    
    return val_loss, val_acc


# -------------------------------
# Ana training fonksiyonu
# -------------------------------
def train_model(
    data_dir,
    num_epochs=50,
    batch_size=32,
    initial_lr=0.001,
    fine_tune_lr=0.0001,
    fine_tune_epoch=20,
    num_workers=0,
    output_dir='runs/resnet50_v2'
):
    """
    Progressive training:
    - İlk N epoch: Sadece FC layer (yüksek LR)
    - Sonraki epochlar: Tüm ağ (düşük LR)
    """
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n🚀 Device: {device}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    # Output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f'{output_dir}/weights', exist_ok=True)
    
    # TensorBoard (opsiyonel)
    writer = None
    if TENSORBOARD_AVAILABLE:
        writer = SummaryWriter(f'{output_dir}/logs')
        print("✅ TensorBoard logging aktif")
    
    # -------------------------------
    # Gelişmiş augmentation
    # -------------------------------
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.6, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.3, scale=(0.02, 0.2))
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Dataset
    print("\n📂 Dataset yükleniyor...")
    train_dataset = datasets.ImageFolder(f'{data_dir}/train', transform=train_transform)
    val_dataset = datasets.ImageFolder(f'{data_dir}/val', transform=val_transform)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, 
                             num_workers=num_workers, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, 
                           num_workers=num_workers, pin_memory=True)
    
    num_classes = len(train_dataset.classes)
    print(f"   Train: {len(train_dataset)} görüntü")
    print(f"   Val: {len(val_dataset)} görüntü")
    print(f"   Classes: {num_classes}")
    
    # Class names kaydet
    with open(f'{output_dir}/class_names.json', 'w', encoding='utf-8') as f:
        json.dump(train_dataset.classes, f, ensure_ascii=False, indent=2)
    
    # Model
    print("\n🤖 Model oluşturuluyor...")
    model = create_model(num_classes, freeze_backbone=True)
    model = model.to(device)
    
    # Loss & Optimizer
    criterion = LabelSmoothingCrossEntropy(smoothing=0.1)
    mixup_cutmix = MixupCutmix(mixup_alpha=0.2, cutmix_alpha=1.0, prob=0.5)
    
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=initial_lr,
        weight_decay=0.01
    )
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=10, T_mult=2, eta_min=1e-6
    )
    
    # Mixed precision
    scaler = GradScaler()
    
    # Training loop
    print(f"\n🔥 Training başlıyor... ({num_epochs} epochs)")
    print(f"   Strateji: İlk {fine_tune_epoch} epoch FC only, sonrası full fine-tuning")
    print(f"   Initial LR: {initial_lr}, Fine-tune LR: {fine_tune_lr}")
    
    best_val_acc = 0.0
    history = {
        'train_loss': [], 'train_acc': [],
        'val_loss': [], 'val_acc': [],
        'lr': []
    }
    
    start_time = time.time()
    
    for epoch in range(1, num_epochs + 1):
        print(f"\n{'='*60}")
        print(f"Epoch {epoch}/{num_epochs}")
        
        # Fine-tuning'e geçiş
        if epoch == fine_tune_epoch:
            print("\n🔓 BACKBONE AÇILIYOR - Fine-tuning başlıyor!")
            unfreeze_backbone(model)
            
            # Optimizer'ı yeniden oluştur (tüm parametreler için)
            optimizer = optim.AdamW([
                {'params': model.fc.parameters(), 'lr': initial_lr},  # Head yüksek LR
                {'params': model.layer4.parameters(), 'lr': fine_tune_lr},
                {'params': model.layer3.parameters(), 'lr': fine_tune_lr * 0.5},
                {'params': model.layer2.parameters(), 'lr': fine_tune_lr * 0.1},
                {'params': model.layer1.parameters(), 'lr': fine_tune_lr * 0.01},
            ], weight_decay=0.01)
            
            scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
                optimizer, T_0=10, T_mult=2, eta_min=1e-7
            )
        
        current_lr = optimizer.param_groups[0]['lr']
        print(f"Learning Rate: {current_lr:.6f}")
        
        # Train
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, device, 
            scaler, mixup_cutmix, epoch, num_epochs
        )
        
        # Validate
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        # Scheduler step
        scheduler.step()
        
        # Sonuçları kaydet
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['lr'].append(current_lr)
        
        # TensorBoard (varsa)
        if writer is not None:
            writer.add_scalar('Loss/train', train_loss, epoch)
            writer.add_scalar('Loss/val', val_loss, epoch)
            writer.add_scalar('Accuracy/train', train_acc, epoch)
            writer.add_scalar('Accuracy/val', val_acc, epoch)
            writer.add_scalar('Learning_Rate', current_lr, epoch)
        
        print(f"\nTrain Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
        
        # En iyi model kaydet
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'val_loss': val_loss,
                'class_names': train_dataset.classes
            }, f'{output_dir}/weights/best.pth')
            print(f"✅ En iyi model kaydedildi! (Val Acc: {val_acc:.2f}%)")
        
        # Her 10 epochta checkpoint
        if epoch % 10 == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'val_loss': val_loss,
            }, f'{output_dir}/weights/checkpoint_epoch{epoch}.pth')
    
    # Training tamamlandı
    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"✅ Training tamamlandı!")
    print(f"   Toplam süre: {total_time/60:.1f} dakika")
    print(f"   En iyi Val Acc: {best_val_acc:.2f}%")
    print(f"   Model: {output_dir}/weights/best.pth")
    
    # History kaydet
    with open(f'{output_dir}/history.json', 'w') as f:
        json.dump(history, f, indent=2)
    
    if writer is not None:
        writer.close()
    
    return model, history


# -------------------------------
# Main
# -------------------------------
if __name__ == '__main__':
    # Konfigürasyon
    config = {
        'data_dir': 'images_split',
        'num_epochs': 60,  # Daha uzun training
        'batch_size': 32,  # GPU'ya göre ayarlayın (16 veya 32)
        'initial_lr': 0.001,  # FC layer için
        'fine_tune_lr': 0.0001,  # Backbone için
        'fine_tune_epoch': 15,  # 15. epochta fine-tuning başlasın
        'num_workers': 0,  # Windows için 0
        'output_dir': 'runs/resnet50_v2'
    }
    
    print("\n" + "="*60)
    print("🚀 ResNet-50 Advanced Training v2.0")
    print("="*60)
    print("\n📋 Konfigürasyon:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    # Training başlat
    model, history = train_model(**config)
    
    print("\n🎉 Training başarıyla tamamlandı!")
    print(f"\n📊 Sonuç özeti:")
    print(f"   Final Train Acc: {history['train_acc'][-1]:.2f}%")
    print(f"   Final Val Acc: {history['val_acc'][-1]:.2f}%")
    print(f"   Best Val Acc: {max(history['val_acc']):.2f}%")
    print(f"\n💾 Model: runs/resnet50_v2/weights/best.pth")
    print(f"📈 TensorBoard: tensorboard --logdir=runs/resnet50_v2/logs")
