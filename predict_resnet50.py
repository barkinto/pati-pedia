"""
predict_resnet50.py

ResNet-50 modeli ile kedi cinsi tahmini yapar.

Kullanım:
  python predict_resnet50.py --image test.jpg
  python predict_resnet50.py --image test.jpg --model runs/resnet50/weights/best.pth
"""

import argparse
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os

def load_model(model_path, device='cuda'):
    """Load trained ResNet-50 model"""
    print(f'Loading model from {model_path}...')
    
    # Load checkpoint
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    num_classes = len(checkpoint['class_names'])
    class_names = checkpoint['class_names']
    
    # Build model architecture
    model = models.resnet50(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    
    # Load weights
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    print(f'Model loaded successfully! ({num_classes} classes)')
    return model, class_names

def predict_image(image_path, model, class_names, device='cuda', top_k=5):
    """Predict cat breed for a single image"""
    
    # Image transforms (same as training)
    transform = transforms.Compose([
        transforms.Resize(int(224 * 1.15)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Load and transform image
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    # Predict
    with torch.no_grad():
        outputs = model(image_tensor)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        top_probs, top_indices = torch.topk(probs, top_k)
    
    # Print results
    print(f"\n{'='*60}")
    print(f"📸 Görsel: {os.path.basename(image_path)}")
    print(f"{'='*60}")
    print(f"\n🏆 Top-{top_k} Tahminler:\n")
    
    for i, (prob, idx) in enumerate(zip(top_probs[0], top_indices[0]), 1):
        breed = class_names[idx]
        confidence = prob.item() * 100
        bar = '█' * int(confidence / 2)
        print(f"{i}. {breed:30s} {confidence:5.2f}% {bar}")
    
    print(f"\n{'='*60}")
    print(f"✅ En Olası Cins: {class_names[top_indices[0][0]]}")
    print(f"{'='*60}\n")
    
    return class_names[top_indices[0][0]], top_probs[0][0].item()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, required=True, help='Path to image file')
    parser.add_argument('--model', type=str, default='runs/resnet50/weights/best.pth', help='Path to model checkpoint')
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--top-k', type=int, default=5, help='Show top K predictions')
    args = parser.parse_args()
    
    # Check if image exists
    if not os.path.exists(args.image):
        print(f"❌ Error: Image file not found: {args.image}")
        return
    
    # Check if model exists
    if not os.path.exists(args.model):
        print(f"❌ Error: Model file not found: {args.model}")
        return
    
    print(f"Using device: {args.device}")
    
    # Load model
    model, class_names = load_model(args.model, args.device)
    
    # Predict
    breed, confidence = predict_image(args.image, model, class_names, args.device, args.top_k)

if __name__ == '__main__':
    main()
