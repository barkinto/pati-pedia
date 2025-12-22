"""
Ensemble Model - ResNet50 + EfficientNetB3 + ConvNeXt
Stacking approach with meta-learner
"""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import List, Tuple

class ResNet50Classifier(nn.Module):
    """ResNet-50 Model with Advanced Regularization"""
    def __init__(self, num_classes=59, dropout=0.5):
        super().__init__()
        self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        num_ftrs = self.model.fc.in_features
        
        # 🔥 Multi-layer Dropout Classifier (daha güçlü regularization)
        self.model.fc = nn.Sequential(
            nn.Dropout(dropout * 0.5),  # First dropout: 25%
            nn.Linear(num_ftrs, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout),  # Second dropout: 50%
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)
    
    def get_features(self, x):
        """Extract features before final FC layer"""
        x = self.model.conv1(x)
        x = self.model.bn1(x)
        x = self.model.relu(x)
        x = self.model.maxpool(x)
        x = self.model.layer1(x)
        x = self.model.layer2(x)
        x = self.model.layer3(x)
        x = self.model.layer4(x)
        x = self.model.avgpool(x)
        x = torch.flatten(x, 1)
        return x


class EfficientNetB3Classifier(nn.Module):
    """EfficientNet-B3 Model with Advanced Regularization"""
    def __init__(self, num_classes=59, dropout=0.5):
        super().__init__()
        self.model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.IMAGENET1K_V1)
        num_ftrs = self.model.classifier[1].in_features
        
        # 🔥 Multi-layer Dropout Classifier
        self.model.classifier = nn.Sequential(
            nn.Dropout(dropout * 0.5),
            nn.Linear(num_ftrs, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)
    
    def get_features(self, x):
        """Extract features before final classifier"""
        x = self.model.features(x)
        x = self.model.avgpool(x)
        x = torch.flatten(x, 1)
        return x


class ConvNeXtClassifier(nn.Module):
    """ConvNeXt-Tiny Model with Advanced Regularization"""
    def __init__(self, num_classes=59, dropout=0.5):
        super().__init__()
        self.model = models.convnext_tiny(weights=models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1)
        num_ftrs = self.model.classifier[2].in_features
        
        # 🔥 Multi-layer Dropout Classifier
        self.model.classifier = nn.Sequential(
            self.model.classifier[0],  # LayerNorm
            self.model.classifier[1],  # Flatten
            nn.Dropout(dropout * 0.5),
            nn.Linear(num_ftrs, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)
    
    def get_features(self, x):
        """Extract features before final classifier"""
        x = self.model.features(x)
        x = self.model.avgpool(x)
        x = torch.flatten(x, 1)
        return x


class MetaLearner(nn.Module):
    """
    Meta-learner that combines predictions from base models
    """
    def __init__(self, num_classes=59, feature_dim=3):
        super().__init__()
        # Input: concatenated probabilities from 3 models (59*3 = 177)
        self.fc = nn.Sequential(
            nn.Linear(num_classes * feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        return self.fc(x)


class StackingEnsemble(nn.Module):
    """
    Stacking Ensemble: ResNet50 + EfficientNetB3 + ConvNeXt + Meta-Learner
    """
    def __init__(self, num_classes=59, dropout=0.5, device='cuda'):
        super().__init__()
        self.num_classes = num_classes
        self.device = device
        
        # Base models
        self.resnet50 = ResNet50Classifier(num_classes, dropout)
        self.efficientnet = EfficientNetB3Classifier(num_classes, dropout)
        self.convnext = ConvNeXtClassifier(num_classes, dropout)
        
        # Meta-learner
        self.meta_learner = MetaLearner(num_classes, feature_dim=3)
        
        self.models = [self.resnet50, self.efficientnet, self.convnext]
        self.model_names = ['ResNet50', 'EfficientNetB3', 'ConvNeXt']
    
    def forward(self, x, use_meta=True):
        """
        Forward pass through ensemble
        
        Args:
            x: Input tensor
            use_meta: If True, use meta-learner; if False, use simple averaging
        
        Returns:
            Final predictions
        """
        # Get predictions from all base models
        pred1 = self.resnet50(x)
        pred2 = self.efficientnet(x)
        pred3 = self.convnext(x)
        
        if use_meta:
            # Stack predictions and pass through meta-learner
            stacked = torch.cat([pred1, pred2, pred3], dim=1)
            output = self.meta_learner(stacked)
        else:
            # Simple averaging
            output = (pred1 + pred2 + pred3) / 3.0
        
        return output
    
    def predict_with_details(self, x):
        """
        Get predictions from each model + ensemble
        
        Returns:
            Dictionary with all predictions
        """
        with torch.no_grad():
            pred_resnet = torch.softmax(self.resnet50(x), dim=1)
            pred_efficient = torch.softmax(self.efficientnet(x), dim=1)
            pred_convnext = torch.softmax(self.convnext(x), dim=1)
            
            # Meta-learner prediction
            stacked = torch.cat([
                self.resnet50(x), 
                self.efficientnet(x), 
                self.convnext(x)
            ], dim=1)
            pred_ensemble = torch.softmax(self.meta_learner(stacked), dim=1)
            
            return {
                'ResNet50': pred_resnet,
                'EfficientNetB3': pred_efficient,
                'ConvNeXt': pred_convnext,
                'Ensemble': pred_ensemble
            }
    
    def load_base_models(self, resnet_path, efficient_path, convnext_path):
        """Load pretrained weights for base models"""
        print(f"Loading ResNet50 from {resnet_path}")
        self.resnet50.load_state_dict(torch.load(resnet_path, map_location=self.device))
        
        print(f"Loading EfficientNetB3 from {efficient_path}")
        self.efficientnet.load_state_dict(torch.load(efficient_path, map_location=self.device))
        
        print(f"Loading ConvNeXt from {convnext_path}")
        self.convnext.load_state_dict(torch.load(convnext_path, map_location=self.device))
        
        print("All base models loaded successfully!")
    
    def freeze_base_models(self):
        """Freeze base models for meta-learner training"""
        for model in self.models:
            for param in model.parameters():
                param.requires_grad = False
        print("Base models frozen")
    
    def unfreeze_base_models(self):
        """Unfreeze base models for fine-tuning"""
        for model in self.models:
            for param in model.parameters():
                param.requires_grad = True
        print("Base models unfrozen")


def create_ensemble(num_classes=59, dropout=0.5, device='cuda'):
    """Factory function to create ensemble model"""
    model = StackingEnsemble(num_classes, dropout, device)
    return model


if __name__ == "__main__":
    # Test
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")
    
    model = create_ensemble(num_classes=59, device=device)
    model = model.to(device)
    
    # Test forward pass
    dummy_input = torch.randn(2, 3, 224, 224).to(device)
    
    print("\n=== Testing Ensemble ===")
    output = model(dummy_input, use_meta=True)
    print(f"Output shape: {output.shape}")
    
    print("\n=== Testing Detailed Predictions ===")
    details = model.predict_with_details(dummy_input)
    for name, pred in details.items():
        print(f"{name}: {pred.shape}, Top prob: {pred[0].max().item():.4f}")
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n=== Model Stats ===")
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    print(f"Model size: ~{total_params * 4 / 1024 / 1024:.1f} MB")
