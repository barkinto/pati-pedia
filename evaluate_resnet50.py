"""
evaluate_resnet50.py

ResNet-50 modelini test seti üzerinde değerlendirir.
Accuracy, Precision, Recall, F1-Score ve Confusion Matrix hesaplar.

Kullanım:
  python evaluate_resnet50.py --model runs/resnet50/weights/best.pth
"""

import argparse
import torch
import torch.nn as nn
from torchvision import models, transforms, datasets
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import os

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
    
    print(f'✅ Model loaded! ({num_classes} classes)')
    return model, class_names

def evaluate_model(model, dataloader, device='cuda'):
    """Evaluate model and return predictions and labels"""
    all_preds = []
    all_labels = []
    all_probs = []
    
    print('\n🔍 Evaluating model...')
    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc='Batches'):
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    return np.array(all_preds), np.array(all_labels), np.array(all_probs)

def plot_confusion_matrix(cm, class_names, save_path='confusion_matrix.png'):
    """Plot and save confusion matrix"""
    plt.figure(figsize=(20, 18))
    
    # Normalize confusion matrix
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    # Plot with annotations for top breeds only (for readability)
    sns.heatmap(cm_norm, annot=False, fmt='.2f', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names,
                cbar_kws={'label': 'Normalized Count'})
    
    plt.title('Confusion Matrix (Normalized)', fontsize=16, pad=20)
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.xticks(rotation=90, ha='right', fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f'📊 Confusion matrix saved to {save_path}')
    plt.close()

def plot_top_k_accuracy(probs, labels, class_names, k_values=[1, 3, 5, 10], save_path='top_k_accuracy.png'):
    """Plot top-k accuracy"""
    accuracies = []
    
    for k in k_values:
        top_k_preds = np.argsort(probs, axis=1)[:, -k:]
        correct = sum([labels[i] in top_k_preds[i] for i in range(len(labels))])
        acc = correct / len(labels) * 100
        accuracies.append(acc)
    
    plt.figure(figsize=(10, 6))
    plt.bar([f'Top-{k}' for k in k_values], accuracies, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    plt.ylabel('Accuracy (%)', fontsize=12)
    plt.xlabel('Top-K', fontsize=12)
    plt.title('Top-K Accuracy', fontsize=14, pad=15)
    plt.ylim([0, 105])
    
    for i, (k, acc) in enumerate(zip(k_values, accuracies)):
        plt.text(i, acc + 2, f'{acc:.2f}%', ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f'📊 Top-k accuracy plot saved to {save_path}')
    plt.close()
    
    return dict(zip([f'top_{k}' for k in k_values], accuracies))

def plot_per_class_accuracy(cm, class_names, save_path='per_class_accuracy.png', top_n=20):
    """Plot per-class accuracy for top N classes"""
    per_class_acc = cm.diagonal() / cm.sum(axis=1)
    
    # Get top N and bottom N classes
    sorted_indices = np.argsort(per_class_acc)
    top_indices = sorted_indices[-top_n:]
    
    plt.figure(figsize=(12, 8))
    y_pos = np.arange(top_n)
    
    plt.barh(y_pos, per_class_acc[top_indices] * 100, color='steelblue')
    plt.yticks(y_pos, [class_names[i] for i in top_indices], fontsize=9)
    plt.xlabel('Accuracy (%)', fontsize=12)
    plt.title(f'Top-{top_n} Class Accuracies', fontsize=14, pad=15)
    plt.xlim([0, 105])
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f'📊 Per-class accuracy plot saved to {save_path}')
    plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='runs/resnet50/weights/best.pth')
    parser.add_argument('--data', type=str, default='images_split/val')
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--output-dir', type=str, default='runs/resnet50/evaluation')
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"🔬 ResNet-50 Model Evaluation")
    print(f"{'='*60}\n")
    print(f"Model: {args.model}")
    print(f"Data: {args.data}")
    print(f"Device: {args.device}")
    
    # Load model
    model, class_names = load_model(args.model, args.device)
    
    # Prepare data
    transform = transforms.Compose([
        transforms.Resize(int(224 * 1.15)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    dataset = datasets.ImageFolder(args.data, transform=transform)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=4)
    
    print(f"Dataset size: {len(dataset)} images")
    print(f"Number of classes: {len(class_names)}")
    
    # Evaluate
    preds, labels, probs = evaluate_model(model, dataloader, args.device)
    
    # Calculate metrics
    print(f"\n{'='*60}")
    print(f"📈 RESULTS")
    print(f"{'='*60}\n")
    
    # Overall accuracy
    accuracy = accuracy_score(labels, preds) * 100
    print(f"✅ Overall Accuracy: {accuracy:.2f}%\n")
    
    # Top-k accuracy
    top_k_acc = plot_top_k_accuracy(probs, labels, class_names, 
                                     save_path=os.path.join(args.output_dir, 'top_k_accuracy.png'))
    for k, acc in top_k_acc.items():
        print(f"   {k.upper()}: {acc:.2f}%")
    
    # Confusion matrix
    cm = confusion_matrix(labels, preds)
    plot_confusion_matrix(cm, class_names, 
                         save_path=os.path.join(args.output_dir, 'confusion_matrix.png'))
    
    # Per-class accuracy
    plot_per_class_accuracy(cm, class_names, 
                           save_path=os.path.join(args.output_dir, 'per_class_accuracy.png'))
    
    # Classification report
    report = classification_report(labels, preds, target_names=class_names, digits=4, zero_division=0)
    
    # Save report to file
    report_path = os.path.join(args.output_dir, 'classification_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"ResNet-50 Model Evaluation\n")
        f.write(f"{'='*80}\n\n")
        f.write(f"Model: {args.model}\n")
        f.write(f"Dataset: {args.data}\n")
        f.write(f"Total samples: {len(labels)}\n\n")
        f.write(f"Overall Accuracy: {accuracy:.2f}%\n\n")
        f.write(f"Top-K Accuracies:\n")
        for k, acc in top_k_acc.items():
            f.write(f"  {k.upper()}: {acc:.2f}%\n")
        f.write(f"\n{'='*80}\n")
        f.write(f"CLASSIFICATION REPORT\n")
        f.write(f"{'='*80}\n\n")
        f.write(report)
    
    print(f"\n📄 Full report saved to {report_path}")
    
    print(f"\n{'='*60}")
    print(f"✅ Evaluation completed!")
    print(f"📁 Results saved to: {args.output_dir}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
