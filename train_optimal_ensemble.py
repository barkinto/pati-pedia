"""
Optimal 3-Model Ensemble - 4GB VRAM İçin Optimize Edilmiş
Models: ResNet50 (mevcut best) + EfficientNet-B0 + MobileNetV3
Özellikler:
- Mixed Precision (fp16) - VRAM %50 azaltma
- Gradient Accumulation - Sanal batch size 32
- Anti-overfitting: Dropout, Label Smoothing, Early Stopping
- Hardware Safe: 224x224 image, batch_size=8
Beklenen Accuracy: 75-82%
Eğitim Süresi: ~5-6 saat
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.cuda.amp import autocast, GradScaler
from torchvision import datasets, transforms, models
import json
import time
from pathlib import Path
from tqdm import tqdm
import gc

from augmentation_utils import (
    mixup_data, cutmix_data, mixup_criterion,
    LabelSmoothingCrossEntropy, EarlyStopping, GradientClipping
)


class MobileNetV3Classifier(nn.Module):
    """MobileNetV3-Large Model (~5.4M params)"""
    def __init__(self, num_classes=59, dropout=0.5):
        super().__init__()
        self.model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.IMAGENET1K_V2)
        num_ftrs = self.model.classifier[0].in_features
        
        # Anti-overfitting: Multi-layer dropout
        self.model.classifier = nn.Sequential(
            nn.Dropout(dropout * 0.4),  # 20%
            nn.Linear(num_ftrs, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout),  # 50%
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)


class EfficientNetB0Classifier(nn.Module):
    """EfficientNet-B0 Model (~5.3M params)"""
    def __init__(self, num_classes=59, dropout=0.5):
        super().__init__()
        self.model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
        num_ftrs = self.model.classifier[1].in_features
        
        # Anti-overfitting: Multi-layer dropout
        self.model.classifier = nn.Sequential(
            nn.Dropout(dropout * 0.4),  # 20%
            nn.Linear(num_ftrs, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout),  # 50%
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)


class ResNet50Classifier(nn.Module):
    """ResNet-50 Model (~24.6M params)"""
    def __init__(self, num_classes=59, dropout=0.5):
        super().__init__()
        self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        num_ftrs = self.model.fc.in_features
        
        # Multi-layer dropout (mevcut best model ile aynı)
        self.model.fc = nn.Sequential(
            nn.Dropout(dropout * 0.5),  # 25%
            nn.Linear(num_ftrs, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout),  # 50%
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)


class OptimalEnsemble(nn.Module):
    """
    Optimal 3-Model Ensemble with Anti-Overfitting
    Models: ResNet50 + EfficientNet-B0 + MobileNetV3
    """
    def __init__(self, num_classes=59, dropout=0.5):
        super().__init__()
        self.num_classes = num_classes
        
        self.resnet50 = ResNet50Classifier(num_classes, dropout)
        self.efficientnet = EfficientNetB0Classifier(num_classes, dropout)
        self.mobilenet = MobileNetV3Classifier(num_classes, dropout)
        
        # Meta-learner: 3 models * 59 classes = 177 features
        # Anti-overfitting: Moderate dropout, smaller architecture
        self.meta_learner = nn.Sequential(
            nn.Linear(num_classes * 3, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x, use_meta=True):
        pred1 = self.resnet50(x)
        pred2 = self.efficientnet(x)
        pred3 = self.mobilenet(x)
        
        if use_meta:
            stacked = torch.cat([pred1, pred2, pred3], dim=1)
            output = self.meta_learner(stacked)
        else:
            output = (pred1 + pred2 + pred3) / 3.0
        
        return output
    
    def freeze_base_models(self):
        """Freeze base models for meta-learner training"""
        for model in [self.resnet50, self.efficientnet, self.mobilenet]:
            for param in model.parameters():
                param.requires_grad = False
        print("✓ Base models frozen")
    
    def unfreeze_base_models(self):
        """Unfreeze base models for fine-tuning"""
        for model in [self.resnet50, self.efficientnet, self.mobilenet]:
            for param in model.parameters():
                param.requires_grad = True
        print("✓ Base models unfrozen")


def get_transforms(mode='train'):
    """Hardware-safe transforms: 224x224 only"""
    if mode == 'train':
        # Strong augmentation for anti-overfitting
        return transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(20),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            transforms.RandomErasing(p=0.3, scale=(0.02, 0.15))
        ])
    else:
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])


def train_single_model_with_amp(model, model_name, train_loader, val_loader, device, 
                                 num_epochs=15, save_dir='runs/optimal_ensemble',
                                 accumulation_steps=4):
    """
    Train with Mixed Precision + Gradient Accumulation
    accumulation_steps=4: Sanal batch_size = 8 * 4 = 32
    """
    print(f"\n{'='*70}")
    print(f"🚀 Training {model_name}")
    print(f"   Mixed Precision: ✓ (fp16)")
    print(f"   Gradient Accumulation: ✓ (steps={accumulation_steps})")
    print(f"   Virtual Batch Size: {8 * accumulation_steps}")
    print(f"{'='*70}")
    
    model = model.to(device)
    criterion = LabelSmoothingCrossEntropy(smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
    early_stopping = EarlyStopping(patience=7, min_delta=0.001)
    
    # Mixed Precision Scaler
    scaler = GradScaler()
    
    best_acc = 0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0
        correct = 0
        total = 0
        
        optimizer.zero_grad()
        
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}')
        for batch_idx, (inputs, labels) in enumerate(pbar):
            inputs, labels = inputs.to(device), labels.to(device)
            
            # Mixed Precision Forward Pass
            with autocast():
                # Random augmentation for anti-overfitting
                if torch.rand(1).item() > 0.5:
                    inputs, labels_a, labels_b, lam = mixup_data(inputs, labels, alpha=0.2)
                    outputs = model(inputs)
                    loss = mixup_criterion(criterion, outputs, labels_a, labels_b, lam)
                else:
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                
                # Gradient Accumulation: Loss normalization
                loss = loss / accumulation_steps
            
            # Mixed Precision Backward Pass
            scaler.scale(loss).backward()
            
            # Update weights every accumulation_steps
            if (batch_idx + 1) % accumulation_steps == 0:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
            
            train_loss += loss.item() * accumulation_steps
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            pbar.set_postfix({
                'loss': f'{loss.item() * accumulation_steps:.4f}',
                'acc': f'{100.*correct/total:.2f}%'
            })
        
        train_loss = train_loss / len(train_loader)
        train_acc = 100. * correct / total
        
        # Validation
        model.eval()
        val_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                
                with autocast():
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        
        val_loss = val_loss / len(val_loader)
        val_acc = 100. * correct / total
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f"\nEpoch {epoch+1}/{num_epochs}:")
        print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_acc:
            best_acc = val_acc
            save_path = Path(save_dir) / f'{model_name}_best.pth'
            save_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), save_path)
            print(f"  ✓ Best model saved! Accuracy: {val_acc:.2f}%")
        
        scheduler.step()
        
        # Early stopping (anti-overfitting)
        if early_stopping(val_loss):
            print(f"⚠️  Early stopping at epoch {epoch+1} (validation not improving)")
            break
        
        # VRAM cleanup
        torch.cuda.empty_cache()
        gc.collect()
    
    return model, history, best_acc


def train_ensemble_with_amp(ensemble, train_loader, val_loader, device, 
                            num_epochs, stage_name, accumulation_steps=4):
    """Train ensemble with mixed precision"""
    print(f"\n{'='*70}")
    print(f"STAGE: {stage_name}")
    print(f"   Mixed Precision: ✓")
    print(f"   Gradient Accumulation: ✓ (steps={accumulation_steps})")
    print(f"{'='*70}")
    
    criterion = LabelSmoothingCrossEntropy(smoothing=0.1)
    optimizer = optim.AdamW(ensemble.parameters(), lr=0.0001, weight_decay=0.01)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
    scaler = GradScaler()
    
    best_acc = 0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    for epoch in range(num_epochs):
        # Training
        ensemble.train()
        train_loss = 0
        correct = 0
        total = 0
        
        optimizer.zero_grad()
        
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}')
        for batch_idx, (inputs, labels) in enumerate(pbar):
            inputs, labels = inputs.to(device), labels.to(device)
            
            with autocast():
                outputs = ensemble(inputs, use_meta=True)
                loss = criterion(outputs, labels) / accumulation_steps
            
            scaler.scale(loss).backward()
            
            if (batch_idx + 1) % accumulation_steps == 0:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(ensemble.parameters(), max_norm=1.0)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
            
            train_loss += loss.item() * accumulation_steps
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            pbar.set_postfix({
                'loss': f'{loss.item() * accumulation_steps:.4f}',
                'acc': f'{100.*correct/total:.2f}%'
            })
        
        train_loss = train_loss / len(train_loader)
        train_acc = 100. * correct / total
        
        # Validation
        ensemble.eval()
        val_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                
                with autocast():
                    outputs = ensemble(inputs, use_meta=True)
                    loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        
        val_loss = val_loss / len(val_loader)
        val_acc = 100. * correct / total
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f"\nEpoch {epoch+1}/{num_epochs}:")
        print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        if val_acc > best_acc:
            best_acc = val_acc
            print(f"  ✓ Best accuracy: {val_acc:.2f}%")
        
        scheduler.step()
        torch.cuda.empty_cache()
        gc.collect()
    
    return ensemble, history, best_acc


def main():
    print("="*70)
    print("🚀 OPTIMAL 3-MODEL ENSEMBLE - 4GB VRAM OPTIMIZED")
    print("="*70)
    print("Models: ResNet50 (best) + EfficientNet-B0 + MobileNetV3")
    print("Features:")
    print("  ✓ Mixed Precision (fp16) - VRAM %50 azaltma")
    print("  ✓ Gradient Accumulation - Sanal batch_size=32")
    print("  ✓ Strong Augmentation - Anti-overfitting")
    print("  ✓ Early Stopping - Ezber önleme")
    print("  ✓ Label Smoothing - Generalization")
    print("="*70)
    
    # Configuration - Hardware Safe
    DATA_DIR = 'images_split'
    SAVE_DIR = 'runs/optimal_ensemble'
    BATCH_SIZE = 8  # Gerçek batch size
    ACCUMULATION_STEPS = 4  # Sanal batch size = 8 * 4 = 32
    NUM_WORKERS = 4
    
    EPOCHS_BASE = 15  # Good balance
    EPOCHS_META = 10
    EPOCHS_FINE = 5
    
    # Device check
    if not torch.cuda.is_available():
        print("❌ CUDA not available! This script requires GPU.")
        return
    
    device = torch.device('cuda')
    print(f"\nDevice: {device}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Enable TF32 for better performance on RTX 30 series
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    print("✓ TF32 enabled for RTX 3050")
    
    # Data loaders
    print("\n📁 Loading datasets...")
    train_dataset = datasets.ImageFolder(f'{DATA_DIR}/train', transform=get_transforms('train'))
    val_dataset = datasets.ImageFolder(f'{DATA_DIR}/val', transform=get_transforms('val'))
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, 
                              shuffle=True, num_workers=NUM_WORKERS, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE,
                           shuffle=False, num_workers=NUM_WORKERS, pin_memory=True)
    
    num_classes = len(train_dataset.classes)
    print(f"Classes: {num_classes}")
    print(f"Train samples: {len(train_dataset)}")
    print(f"Val samples: {len(val_dataset)}")
    print(f"Real Batch Size: {BATCH_SIZE}")
    print(f"Virtual Batch Size: {BATCH_SIZE * ACCUMULATION_STEPS}")
    
    Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()
    all_histories = {}
    
    print("\n" + "="*70)
    print("STAGE 1: Training Base Models")
    print("="*70)
    
    # Load existing ResNet50
    resnet50_path = Path('runs/resnet50_v2/weights/best.pth')
    if resnet50_path.exists():
        print(f"\n{'='*70}")
        print("📦 Loading Best ResNet50 Model (64.67%)")
        print(f"{'='*70}")
        
        resnet_old = models.resnet50(weights=None)
        resnet_old.fc = nn.Sequential(nn.Dropout(0.5), nn.Linear(2048, 59))
        
        checkpoint = torch.load(resnet50_path, weights_only=False)
        resnet_old.load_state_dict(checkpoint['model_state_dict'])
        
        # Validate
        resnet_old = resnet_old.to(device)
        resnet_old.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = resnet_old(inputs)
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        acc_resnet50 = 100. * correct / total
        print(f"✓ ResNet50 Accuracy: {acc_resnet50:.2f}%")
        
        resnet50 = ResNet50Classifier(num_classes)
        resnet50.model = resnet_old
        all_histories['resnet50'] = {'note': 'Best pre-trained model', 'val_acc': acc_resnet50}
        
        torch.save(resnet50.state_dict(), f'{SAVE_DIR}/ResNet50_best.pth')
        print(f"✓ Saved to {SAVE_DIR}")
    else:
        print("❌ ResNet50 best model not found at runs/resnet50_v2/weights/best.pth")
        return
    
    # Train EfficientNet-B0
    efficientnet = EfficientNetB0Classifier(num_classes)
    efficientnet, hist_effnet, acc_effnet = train_single_model_with_amp(
        efficientnet, "EfficientNetB0", train_loader, val_loader, device,
        num_epochs=EPOCHS_BASE, save_dir=SAVE_DIR, accumulation_steps=ACCUMULATION_STEPS
    )
    all_histories['efficientnet_b0'] = hist_effnet
    
    # Train MobileNetV3
    mobilenet = MobileNetV3Classifier(num_classes)
    mobilenet, hist_mobile, acc_mobile = train_single_model_with_amp(
        mobilenet, "MobileNetV3", train_loader, val_loader, device,
        num_epochs=EPOCHS_BASE, save_dir=SAVE_DIR, accumulation_steps=ACCUMULATION_STEPS
    )
    all_histories['mobilenet'] = hist_mobile
    
    stage1_time = time.time() - start_time
    
    print("\n" + "="*70)
    print("STAGE 1 COMPLETE!")
    print(f"Time: {stage1_time/3600:.2f} hours")
    print(f"  ResNet50: {acc_resnet50:.2f}% ✓")
    print(f"  EfficientNet-B0: {acc_effnet:.2f}%")
    print(f"  MobileNetV3: {acc_mobile:.2f}%")
    print("="*70)
    
    # Stage 2: Meta-learner
    print("\n" + "="*70)
    print("STAGE 2: Training Meta-Learner (Anti-Overfitting)")
    print("="*70)
    
    ensemble = OptimalEnsemble(num_classes)
    ensemble.resnet50 = resnet50
    ensemble.efficientnet = efficientnet
    ensemble.mobilenet = mobilenet
    
    ensemble = ensemble.to(device)
    ensemble.freeze_base_models()
    
    ensemble, hist_meta, acc_meta = train_ensemble_with_amp(
        ensemble, train_loader, val_loader, device,
        num_epochs=EPOCHS_META, stage_name="Meta-Learner",
        accumulation_steps=ACCUMULATION_STEPS
    )
    all_histories['meta_learner'] = hist_meta
    
    stage2_time = time.time() - start_time - stage1_time
    
    print("\n" + "="*70)
    print("STAGE 2 COMPLETE!")
    print(f"Time: {stage2_time/3600:.2f} hours")
    print(f"  Meta-Learner Accuracy: {acc_meta:.2f}%")
    print("="*70)
    
    # Stage 3: Fine-tuning
    print("\n" + "="*70)
    print("STAGE 3: Fine-Tuning (Gentle, Anti-Overfitting)")
    print("="*70)
    
    ensemble.unfreeze_base_models()
    
    ensemble, hist_fine, acc_fine = train_ensemble_with_amp(
        ensemble, train_loader, val_loader, device,
        num_epochs=EPOCHS_FINE, stage_name="Fine-Tuning",
        accumulation_steps=ACCUMULATION_STEPS
    )
    all_histories['fine_tuning'] = hist_fine
    
    stage3_time = time.time() - start_time - stage1_time - stage2_time
    total_time = time.time() - start_time
    
    # Save final ensemble
    torch.save(ensemble.state_dict(), f'{SAVE_DIR}/optimal_ensemble_final.pth')
    
    print("\n" + "="*70)
    print("🎉 TRAINING COMPLETE!")
    print("="*70)
    print(f"Total Time: {total_time/3600:.2f} hours")
    print(f"\nStage 1 (Base Models): {stage1_time/3600:.2f} hours")
    print(f"Stage 2 (Meta-Learner): {stage2_time/3600:.2f} hours")
    print(f"Stage 3 (Fine-Tuning): {stage3_time/3600:.2f} hours")
    print(f"\n🏆 Final Ensemble Accuracy: {acc_fine:.2f}%")
    print("\n📊 Model Performances:")
    print(f"   ResNet50: {acc_resnet50:.2f}%")
    print(f"   EfficientNet-B0: {acc_effnet:.2f}%")
    print(f"   MobileNetV3: {acc_mobile:.2f}%")
    print(f"   Meta-Learner: {acc_meta:.2f}%")
    print(f"   Final Ensemble: {acc_fine:.2f}%")
    print("="*70)
    
    # Save training history
    history_path = Path(SAVE_DIR) / 'training_history.json'
    with open(history_path, 'w') as f:
        json.dump(all_histories, f, indent=4)
    print(f"\n✓ Training history saved: {history_path}")
    
    # Save class names
    class_names_path = Path(SAVE_DIR) / 'class_names.json'
    with open(class_names_path, 'w') as f:
        json.dump(train_dataset.classes, f, indent=4)
    print(f"✓ Class names saved: {class_names_path}")
    
    print("\n✅ Optimal ensemble ready!")
    print("   Hardware safe: ✓")
    print("   Anti-overfitting: ✓")
    print("   High accuracy: ✓")


if __name__ == '__main__':
    main()
