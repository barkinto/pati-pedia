"""
train_resnet50.py

Train a ResNet-50 classifier (ImageNet-pretrained) on the project's
`images_split/train` and `images_split/val` folders using torchvision ImageFolder.

Saves best and last checkpoints to `runs/resnet50/weights/`.

Usage examples:
  .\.venv\Scripts\python.exe train_resnet50.py --epochs 20 --batch 32 --device 0

This script is conservative (small defaults) and prints progress to stdout.
"""

import os
import argparse
from pathlib import Path
import time
import copy
import warnings

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.transforms as T
import torchvision.datasets as datasets
import torchvision.models as models
from PIL import Image, ImageFile

# Bozuk JPEG görsellerini tolerans ile yükle
ImageFile.LOAD_TRUNCATED_IMAGES = True
warnings.filterwarnings('ignore', category=UserWarning)


def robust_collate_fn(batch):
    """Collate function that skips None items (from failed image loads)"""
    batch = [item for item in batch if item is not None]
    if len(batch) == 0:
        return None
    return torch.utils.data.dataloader.default_collate(batch)


class RobustImageFolder(datasets.ImageFolder):
    """ImageFolder that returns None for corrupt images instead of crashing"""
    def __getitem__(self, index):
        try:
            path, target = self.samples[index]
            sample = self.loader(path)
            if self.transform is not None:
                sample = self.transform(sample)
            if self.target_transform is not None:
                target = self.target_transform(target)
            return sample, target
        except Exception as e:
            # Return None for corrupt images - will be filtered by collate_fn
            print(f'⚠ Skipping corrupt image: {self.samples[index][0]}')
            return None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='images_split', help='root data folder with train/ val/ subfolders')
    parser.add_argument('--epochs', type=int, default=20, help='number of epochs (default: 20)')
    parser.add_argument('--batch', type=int, default=32)
    parser.add_argument('--img-size', type=int, default=224)
    parser.add_argument('--num-workers', type=int, default=4, help='dataloader workers (4 recommended, 0 for Windows issues)')
    parser.add_argument('--lr', type=float, default=1e-3, help='learning rate for Adam optimizer')
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--output', type=str, default='runs/resnet50')
    parser.add_argument('--resume', type=str, default=None, help='path to checkpoint to resume')
    parser.add_argument('--save-every', type=int, default=1, help='save checkpoint every N epochs')
    parser.add_argument('--freeze-backbone', action='store_true', default=True, help='freeze pretrained layers (transfer learning)')
    return parser.parse_args()


class SafeDataLoader:
    """Wrapper around DataLoader that catches exceptions and skips bad batches"""
    def __init__(self, dataloader):
        self.dataloader = dataloader
        self.dataset = dataloader.dataset
        
    def __iter__(self):
        iterator = iter(self.dataloader)
        while True:
            try:
                batch = next(iterator)
                if batch is not None:
                    yield batch
            except StopIteration:
                break
            except Exception as e:
                print(f'⚠ Skipping batch due to error: {str(e)[:100]}')
                continue
                
    def __len__(self):
        return len(self.dataloader)


def create_dataloaders(data_dir, img_size=224, batch_size=32, num_workers=4):
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')

    print(f'Scanning dataset directories (this may take a moment on first run)...')
    
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    train_tf = T.Compose([
        T.Resize(int(img_size * 1.15)),
        T.RandomResizedCrop(img_size),
        T.RandomHorizontalFlip(),
        T.ToTensor(),
        T.Normalize(mean=mean, std=std),
    ])

    val_tf = T.Compose([
        T.Resize(int(img_size * 1.15)),
        T.CenterCrop(img_size),
        T.ToTensor(),
        T.Normalize(mean=mean, std=std),
    ])

    print(f'  Loading train dataset from {train_dir}...')
    train_ds = RobustImageFolder(train_dir, transform=train_tf)
    print(f'  Found {len(train_ds)} train images')
    
    print(f'  Loading val dataset from {val_dir}...')
    val_ds = RobustImageFolder(val_dir, transform=val_tf)
    print(f'  Found {len(val_ds)} val images')

    train_loader = DataLoader(
        train_ds, 
        batch_size=batch_size, 
        shuffle=True, 
        num_workers=num_workers, 
        pin_memory=True,
        collate_fn=robust_collate_fn
    )
    val_loader = DataLoader(
        val_ds, 
        batch_size=batch_size, 
        shuffle=False, 
        num_workers=num_workers, 
        pin_memory=True,
        collate_fn=robust_collate_fn
    )
    
    # Wrap with SafeDataLoader to catch any remaining exceptions
    train_loader = SafeDataLoader(train_loader)
    val_loader = SafeDataLoader(val_loader)

    class_names = train_ds.classes
    num_classes = len(class_names)

    return train_loader, val_loader, num_classes, class_names


def build_model(num_classes, device, freeze_backbone=True):
    """
    Build ResNet-50 with transfer learning:
    - Load pretrained weights from ImageNet
    - Freeze backbone layers (if freeze_backbone=True)
    - Replace final FC layer with new one for num_classes
    """
    model = models.resnet50(pretrained=True)
    
    # Freeze all backbone parameters for transfer learning
    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False
    
    # Replace final fc layer
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    # FC layer parameters are trainable by default
    
    model = model.to(device)
    return model


def train_one_epoch(model, loader, criterion, optimizer, device, epoch_num=0):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    skipped = 0
    num_batches = len(loader)
    print(f'  Training: {num_batches} batches...')
    
    for batch_idx, batch in enumerate(loader):
        if batch is None:  # Skip empty batches (all images were corrupt)
            skipped += 1
            continue
        try:
            images, targets = batch
            images = images.to(device)
            targets = targets.to(device)

            outputs = model(images)
            loss = criterion(outputs, targets)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = outputs.max(1)
            correct += (preds == targets).sum().item()
            total += images.size(0)
            
            # Progress indicator every 500 batches
            if (batch_idx + 1) % 500 == 0:
                print(f'    Batch {batch_idx+1}/{num_batches}  loss={loss.item():.4f}')
                
        except Exception as e:
            skipped += 1
            if skipped <= 3:
                print(f'Warning: Skipped batch {batch_idx} due to error: {e}')
            continue

    if skipped > 0:
        print(f'Total skipped batches: {skipped}')
    
    epoch_loss = running_loss / total if total > 0 else 0
    epoch_acc = correct / total if total > 0 else 0
    return epoch_loss, epoch_acc


def validate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    skipped = 0
    with torch.no_grad():
        for batch_idx, batch in enumerate(loader):
            if batch is None:  # Skip empty batches
                skipped += 1
                continue
            try:
                images, targets = batch
                images = images.to(device)
                targets = targets.to(device)

                outputs = model(images)
                loss = criterion(outputs, targets)

                running_loss += loss.item() * images.size(0)
                _, preds = outputs.max(1)
                correct += (preds == targets).sum().item()
                total += images.size(0)
            except Exception as e:
                skipped += 1
                if skipped <= 3:
                    print(f'Warning: Skipped validation batch {batch_idx} due to error: {e}')
                continue

    if skipped > 0:
        print(f'Total skipped validation batches: {skipped}')
    
    epoch_loss = running_loss / total if total > 0 else 0
    epoch_acc = correct / total if total > 0 else 0
    return epoch_loss, epoch_acc


def save_checkpoint(state, is_best, output_dir, epoch):
    os.makedirs(os.path.join(output_dir, 'weights'), exist_ok=True)
    ckpt_path = os.path.join(output_dir, 'weights', f'epoch_{epoch}.pth')
    torch.save(state, ckpt_path)
    if is_best:
        best_path = os.path.join(output_dir, 'weights', 'best.pth')
        torch.save(state, best_path)


def main():
    args = parse_args()
    print('Args:', args)

    train_loader, val_loader, num_classes, class_names = create_dataloaders(args.data, img_size=args.img_size, batch_size=args.batch, num_workers=args.num_workers)
    print(f'Found {num_classes} classes. Example: {class_names[:5]}')

    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    model = build_model(num_classes, device, freeze_backbone=args.freeze_backbone)
    
    # Print trainable parameters info
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f'Total parameters: {total_params:,}')
    print(f'Trainable parameters: {trainable_params:,}')
    if args.freeze_backbone:
        print('Transfer learning: backbone frozen, training only final FC layer')

    criterion = nn.CrossEntropyLoss()
    
    # Use Adam optimizer as specified
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), 
                          lr=args.lr, 
                          weight_decay=1e-4)
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    start_epoch = 0
    best_val_loss = float('inf')

    if args.resume:
        print('Resuming from', args.resume)
        ckpt = torch.load(args.resume, map_location=device)
        model.load_state_dict(ckpt['model_state_dict'])
        optimizer.load_state_dict(ckpt['optimizer_state_dict'])
        start_epoch = ckpt.get('epoch', 0) + 1
        best_val_loss = ckpt.get('best_val_loss', best_val_loss)

    os.makedirs(args.output, exist_ok=True)

    print('\nStarting training...')
    for epoch in range(start_epoch, args.epochs):
        t0 = time.time()
        print(f'\nEpoch {epoch+1}/{args.epochs}')
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device, epoch)
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        scheduler.step()

        is_best = val_loss < best_val_loss
        if is_best:
            best_val_loss = val_loss

        state = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_loss': val_loss,
            'best_val_loss': best_val_loss,
            'class_names': class_names,
        }
        if (epoch % args.save_every) == 0 or is_best:
            save_checkpoint(state, is_best, args.output, epoch)

        t1 = time.time()
        print(f'Epoch {epoch+1}/{args.epochs}  time={(t1-t0):.1f}s  train_loss={train_loss:.4f}  train_acc={train_acc:.4f}  val_loss={val_loss:.4f}  val_acc={val_acc:.4f}')

    # Save final last.pth
    last_path = os.path.join(args.output, 'weights', 'last.pth')
    torch.save({'epoch': args.epochs-1, 'model_state_dict': model.state_dict(), 'best_val_loss': best_val_loss, 'class_names': class_names}, last_path)
    print('Training finished. Best val loss:', best_val_loss)


if __name__ == '__main__':
    # Windows multiprocessing fix
    import multiprocessing
    multiprocessing.freeze_support()
    main()
