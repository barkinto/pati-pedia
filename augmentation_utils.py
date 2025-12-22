"""
Advanced Data Augmentation Utilities
Anti-overfitting techniques for better generalization
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

def mixup_data(x, y, alpha=0.4):
    """
    Mixup: Beyond Empirical Risk Minimization (Zhang et al., 2018)
    İki fotoğrafı karıştırarak yeni training sample oluşturur
    
    Args:
        x: input batch
        y: target batch
        alpha: mixup interpolation strength
    
    Returns:
        mixed inputs, pairs of targets, and lambda
    """
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1

    batch_size = x.size()[0]
    index = torch.randperm(batch_size).to(x.device)

    mixed_x = lam * x + (1 - lam) * x[index, :]
    y_a, y_b = y, y[index]
    
    return mixed_x, y_a, y_b, lam


def mixup_criterion(criterion, pred, y_a, y_b, lam):
    """Mixup loss calculation"""
    return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)


def cutmix_data(x, y, alpha=1.0):
    """
    CutMix: Regularization Strategy (Yun et al., 2019)
    Bir fotoğraftan dikdörtgen kesip diğerine yapıştırır
    
    Args:
        x: input batch
        y: target batch
        alpha: cutmix area ratio
    
    Returns:
        mixed inputs, pairs of targets, and lambda
    """
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1

    batch_size = x.size()[0]
    index = torch.randperm(batch_size).to(x.device)

    # Rastgele dikdörtgen alan seç
    _, _, H, W = x.shape
    cut_rat = np.sqrt(1. - lam)
    cut_w = int(W * cut_rat)
    cut_h = int(H * cut_rat)

    # Merkez noktası
    cx = np.random.randint(W)
    cy = np.random.randint(H)

    # Sınırlar
    bbx1 = np.clip(cx - cut_w // 2, 0, W)
    bby1 = np.clip(cy - cut_h // 2, 0, H)
    bbx2 = np.clip(cx + cut_w // 2, 0, W)
    bby2 = np.clip(cy + cut_h // 2, 0, H)

    # CutMix uygula
    x[:, :, bby1:bby2, bbx1:bbx2] = x[index, :, bby1:bby2, bbx1:bbx2]

    # Lambda'yı gerçek alan oranına göre ayarla
    lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (W * H))
    
    y_a, y_b = y, y[index]
    return x, y_a, y_b, lam


class LabelSmoothingCrossEntropy(torch.nn.Module):
    """
    Label Smoothing Cross Entropy
    Hard labels yerine soft labels kullanır
    Örnek: [0, 0, 1, 0] yerine [0.03, 0.03, 0.88, 0.03]
    """
    def __init__(self, smoothing=0.1):
        super().__init__()
        self.smoothing = smoothing
        self.confidence = 1.0 - smoothing

    def forward(self, x, target):
        logprobs = torch.nn.functional.log_softmax(x, dim=-1)
        nll_loss = -logprobs.gather(dim=-1, index=target.unsqueeze(1))
        nll_loss = nll_loss.squeeze(1)
        smooth_loss = -logprobs.mean(dim=-1)
        loss = self.confidence * nll_loss + self.smoothing * smooth_loss
        return loss.mean()


def apply_augmentation_strategy(inputs, targets, strategy='mixup', alpha=0.4):
    """
    Apply selected augmentation strategy
    
    Args:
        inputs: input batch
        targets: target batch
        strategy: 'none', 'mixup', 'cutmix', or 'random'
        alpha: interpolation strength
    
    Returns:
        augmented inputs and targets info
    """
    if strategy == 'none':
        return inputs, targets, None, None, 1.0
    
    elif strategy == 'mixup':
        return mixup_data(inputs, targets, alpha)
    
    elif strategy == 'cutmix':
        return cutmix_data(inputs, targets, alpha)
    
    elif strategy == 'random':
        # Rastgele mixup veya cutmix seç
        if np.random.rand() > 0.5:
            return mixup_data(inputs, targets, alpha)
        else:
            return cutmix_data(inputs, targets, alpha)
    
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


class FocalLoss(nn.Module):
    """
    Focal Loss - Zor örneklere odaklanır
    Hard-to-classify samples'a daha fazla ağırlık verir
    """
    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
    
    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss


class EarlyStopping:
    """
    Early Stopping - Overfitting başladığında eğitimi durdurur
    """
    def __init__(self, patience=5, min_delta=0.001, mode='max'):
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        
    def __call__(self, val_metric):
        if self.best_score is None:
            self.best_score = val_metric
            return False
        
        if self.mode == 'max':
            if val_metric < self.best_score + self.min_delta:
                self.counter += 1
            else:
                self.best_score = val_metric
                self.counter = 0
        else:  # min mode
            if val_metric > self.best_score - self.min_delta:
                self.counter += 1
            else:
                self.best_score = val_metric
                self.counter = 0
        
        if self.counter >= self.patience:
            self.early_stop = True
            return True
        
        return False


class GradientClipping:
    """
    Gradient Clipping - Exploding gradients'ı önler
    """
    @staticmethod
    def clip_gradients(model, max_norm=1.0):
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
        return max_norm


def apply_progressive_resizing(epoch, max_epochs, start_size=128, end_size=224):
    """
    Progressive Resizing - Eğitim sırasında giderek büyüyen fotoğraflar
    İlk epochlarda küçük, son epochlarda büyük
    """
    if epoch < max_epochs // 3:
        return start_size
    elif epoch < 2 * max_epochs // 3:
        return (start_size + end_size) // 2
    else:
        return end_size


class DropBlock2D(nn.Module):
    """
    DropBlock - Dropout'un gelişmiş versiyonu
    Rastgele pikseller yerine bloklarla çalışır
    """
    def __init__(self, drop_prob=0.1, block_size=7):
        super().__init__()
        self.drop_prob = drop_prob
        self.block_size = block_size
    
    def forward(self, x):
        if not self.training or self.drop_prob == 0:
            return x
        
        gamma = self._compute_gamma(x)
        mask = (torch.rand(x.shape[0], x.shape[1], 
                          x.shape[2] - self.block_size + 1,
                          x.shape[3] - self.block_size + 1) < gamma).float()
        
        mask = mask.to(x.device)
        block_mask = self._compute_block_mask(mask)
        
        out = x * block_mask * block_mask.numel() / block_mask.sum()
        return out
    
    def _compute_gamma(self, x):
        return self.drop_prob / (self.block_size ** 2)
    
    def _compute_block_mask(self, mask):
        block_mask = F.max_pool2d(
            input=mask,
            kernel_size=(self.block_size, self.block_size),
            stride=(1, 1),
            padding=self.block_size // 2
        )
        
        if self.block_size % 2 == 0:
            block_mask = block_mask[:, :, :-1, :-1]
        
        block_mask = 1 - block_mask
        return block_mask


# Test
if __name__ == "__main__":
    print("🔥 Augmentation Utilities Test")
    
    # Dummy data
    x = torch.randn(4, 3, 224, 224)
    y = torch.tensor([0, 1, 2, 3])
    
    print("\n1. Mixup Test:")
    mixed_x, y_a, y_b, lam = mixup_data(x, y, alpha=0.4)
    print(f"   Lambda: {lam:.3f}")
    print(f"   y_a: {y_a}, y_b: {y_b}")
    
    print("\n2. CutMix Test:")
    cut_x, y_a, y_b, lam = cutmix_data(x, y, alpha=1.0)
    print(f"   Lambda: {lam:.3f}")
    print(f"   y_a: {y_a}, y_b: {y_b}")
    
    print("\n3. Label Smoothing Test:")
    criterion = LabelSmoothingCrossEntropy(smoothing=0.1)
    pred = torch.randn(4, 10)
    loss = criterion(pred, y)
    print(f"   Loss: {loss.item():.4f}")
    
    print("\n✓ All tests passed!")
