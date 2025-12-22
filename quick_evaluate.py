"""
quick_evaluate.py

ResNet-50 modelini hızlı değerlendirir - minimal dependencies.
"""

import argparse
import torch
import torch.nn as nn
from torchvision import models, transforms, datasets
from torch.utils.data import DataLoader
import numpy as np
from tqdm import tqdm
import os
import multiprocessing
from PIL import Image

class RobustImageFolder(datasets.ImageFolder):
    """ImageFolder that handles corrupt images gracefully"""
    def __getitem__(self, index):
        path, target = self.samples[index]
        try:
            sample = self.loader(path)
            if self.transform is not None:
                sample = self.transform(sample)
            if self.target_transform is not None:
                target = self.target_transform(target)
            return sample, target
        except Exception as e:
            print(f"\nWarning: Skipping corrupt image {path}: {e}")
            return None

def robust_collate_fn(batch):
    """Collate function that filters out None items from corrupt images"""
    batch = [item for item in batch if item is not None]
    if len(batch) == 0:
        return None
    return torch.utils.data.dataloader.default_collate(batch)

def load_model(model_path, device='cuda'):
    """Load trained ResNet-50 model"""
    print(f'Loading model from {model_path}...')
    
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    num_classes = len(checkpoint['class_names'])
    class_names = checkpoint['class_names']
    
    model = models.resnet50(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    print(f'Model loaded successfully!')
    print(f'Number of classes: {num_classes}')
    print(f'Validation loss: {checkpoint["val_loss"]:.4f}')
    
    return model, class_names

def create_dataloader(data_dir, batch_size=32):
    """Create validation dataloader"""
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    dataset = RobustImageFolder(data_dir, transform=transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, 
                           num_workers=0, collate_fn=robust_collate_fn)
    
    return dataloader, dataset.classes

def evaluate_model(model, dataloader, device='cuda'):
    """Evaluate model on validation set"""
    print('\n' + '='*60)
    print('🔍 Evaluating model...')
    print('='*60)
    
    correct_top1 = 0
    correct_top3 = 0
    correct_top5 = 0
    total = 0
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc='Processing batches'):
            if batch is None:  # Skip corrupt batches
                continue
                
            images, labels = batch
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            
            # Top-1 accuracy
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct_top1 += (predicted == labels).sum().item()
            
            # Top-3 accuracy
            _, top3_pred = torch.topk(outputs, 3, dim=1)
            for i in range(labels.size(0)):
                if labels[i] in top3_pred[i]:
                    correct_top3 += 1
            
            # Top-5 accuracy
            _, top5_pred = torch.topk(outputs, 5, dim=1)
            for i in range(labels.size(0)):
                if labels[i] in top5_pred[i]:
                    correct_top5 += 1
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    top1_acc = 100 * correct_top1 / total
    top3_acc = 100 * correct_top3 / total
    top5_acc = 100 * correct_top5 / total
    
    return top1_acc, top3_acc, top5_acc, np.array(all_preds), np.array(all_labels)

def calculate_per_class_accuracy(preds, labels, class_names):
    """Calculate accuracy for each class"""
    per_class_correct = {}
    per_class_total = {}
    
    for i in range(len(class_names)):
        per_class_correct[i] = 0
        per_class_total[i] = 0
    
    for pred, label in zip(preds, labels):
        per_class_total[label] += 1
        if pred == label:
            per_class_correct[label] += 1
    
    per_class_acc = {}
    for i in range(len(class_names)):
        if per_class_total[i] > 0:
            per_class_acc[i] = 100 * per_class_correct[i] / per_class_total[i]
        else:
            per_class_acc[i] = 0.0
    
    return per_class_acc, per_class_total

def main():
    parser = argparse.ArgumentParser(description='Quick Evaluate ResNet-50 Model')
    parser.add_argument('--model', type=str, default='runs/resnet50/weights/best.pth',
                      help='Path to model checkpoint')
    parser.add_argument('--data-dir', type=str, default='images_split/val',
                      help='Path to validation data')
    parser.add_argument('--batch-size', type=int, default=32,
                      help='Batch size for evaluation')
    parser.add_argument('--device', type=str, default='cuda',
                      help='Device to use (cuda/cpu)')
    
    args = parser.parse_args()
    
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    # Load model
    model, model_classes = load_model(args.model, device)
    
    # Create dataloader
    dataloader, data_classes = create_dataloader(args.data_dir, args.batch_size)
    print(f'\nValidation dataset: {len(dataloader.dataset)} images')
    print(f'Number of batches: {len(dataloader)}')
    
    # Evaluate
    top1_acc, top3_acc, top5_acc, preds, labels = evaluate_model(model, dataloader, device)
    
    # Calculate per-class accuracy
    per_class_acc, per_class_total = calculate_per_class_accuracy(preds, labels, model_classes)
    
    # Print results
    print('\n' + '='*60)
    print('📊 EVALUATION RESULTS')
    print('='*60)
    print(f'\n🎯 Overall Accuracy:')
    print(f'  • Top-1: {top1_acc:.2f}%')
    print(f'  • Top-3: {top3_acc:.2f}%')
    print(f'  • Top-5: {top5_acc:.2f}%')
    
    # Find best and worst performing classes
    sorted_classes = sorted(per_class_acc.items(), key=lambda x: x[1], reverse=True)
    
    print(f'\n✨ Best Performing Classes (Top-10):')
    for i, (class_idx, acc) in enumerate(sorted_classes[:10], 1):
        print(f'  {i}. {model_classes[class_idx]}: {acc:.2f}% ({per_class_total[class_idx]} samples)')
    
    print(f'\n⚠️  Worst Performing Classes (Bottom-10):')
    for i, (class_idx, acc) in enumerate(sorted_classes[-10:], 1):
        print(f'  {i}. {model_classes[class_idx]}: {acc:.2f}% ({per_class_total[class_idx]} samples)')
    
    print('\n' + '='*60)
    print('✅ Evaluation completed!')
    print('='*60)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
