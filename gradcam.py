"""
Grad-CAM implementasyonu ResNet50 modeli için
Modelin kararlarını görselleştirmek amacıyla ısı haritası oluşturur
"""

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
import cv2
import io
import base64


class GradCAM:
    """
    Grad-CAM (Gradient-weighted Class Activation Mapping)
    Modelin hangi bölgelere odaklandığını gösteren ısı haritası
    """
    
    def __init__(self, model, target_layer):
        """
        Args:
            model: Eğitilmiş PyTorch modeli
            target_layer: Grad-CAM uygulanacak katman (örn: model.layer4[-1])
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Hook'ları kaydet
        self.target_layer.register_forward_hook(self.save_activations)
        self.target_layer.register_full_backward_hook(self.save_gradients)
    
    def save_activations(self, module, input, output):
        """Forward hook: aktivasyonları kaydet"""
        self.activations = output.detach()
    
    def save_gradients(self, module, grad_input, grad_output):
        """Backward hook: gradientleri kaydet"""
        self.gradients = grad_output[0].detach()
    
    def generate_cam(self, input_tensor, class_idx, device='cuda'):
        """
        CAM (Class Activation Map) oluştur
        
        Args:
            input_tensor: Giriş görseli (batch_size, 3, 224, 224)
            class_idx: Hedef sınıf indeksi
            device: 'cuda' veya 'cpu'
        
        Returns:
            cam: (224, 224) boyutunda NumPy array
        """
        # Forward pass
        output = self.model(input_tensor)
        
        # Backward pass
        self.model.zero_grad()
        target_score = output[0, class_idx]
        target_score.backward()
        
        # Grad-CAM hesapla
        gradients = self.gradients[0]  # (C, H, W)
        activations = self.activations[0]  # (C, H, W)
        
        # Sınıf başına ortalama gradient
        weights = gradients.mean(dim=(1, 2))  # (C,)
        
        # Ağırlıklı kombinasyon
        cam = torch.zeros_like(activations[0])  # (H, W)
        for i in range(len(weights)):
            cam += weights[i] * activations[i]
        
        # ReLU uygula (sadece pozitif etkiler)
        cam = F.relu(cam)
        
        # Normalize et (0-1 aralığı)
        cam_min = cam.min()
        cam_max = cam.max()
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min)
        
        return cam.cpu().numpy()
    
    def overlay_cam_on_image(self, image_array, cam, alpha=0.4):
        """
        CAM'i orijinal görsel üzerine yerleştir
        
        Args:
            image_array: PIL Image veya NumPy array
            cam: (224, 224) CAM array
            alpha: Şeffaflık (0-1)
        
        Returns:
            overlay: Görselleştirilen görsel (PIL Image)
        """
        # Image array'e dönüştür
        if isinstance(image_array, Image.Image):
            img_np = np.array(image_array)
        else:
            img_np = image_array
        
        # CAM'i 224x224 boyutuna yeniden boyutlandır
        cam_resized = cv2.resize(cam, (img_np.shape[1], img_np.shape[0]))
        
        # Isı haritasına dönüştür (sıcak renkler = yüksek aktivasyon)
        heatmap = cv2.applyColorMap((cam_resized * 255).astype(np.uint8), cv2.COLORMAP_JET)
        
        # Orijinal görsel ile birleştir
        overlay = cv2.addWeighted(img_np, 1 - alpha, heatmap, alpha, 0)
        
        return Image.fromarray(overlay)
    
    def generate_visualization(self, image_path, model, class_names, class_idx, device='cuda'):
        """
        Tam görselleştirme pipeline'ı
        
        Args:
            image_path: Görsel dosyası yolu
            model: ResNet50 modeli
            class_names: Sınıf adları listesi
            class_idx: Tahmin edilen sınıf indeksi
            device: 'cuda' veya 'cpu'
        
        Returns:
            overlay_image: PIL Image
            confidence: Güven yüzdesi
        """
        from torchvision import transforms
        
        # Görsel yükle
        image = Image.open(image_path).convert('RGB')
        
        # Transform'ları uygula
        transform = transforms.Compose([
            transforms.Resize(int(224 * 1.15)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform(image).unsqueeze(0).to(device)
        
        # Grad-CAM oluştur
        with torch.no_grad():
            output = model(input_tensor)
            probs = torch.softmax(output, dim=1)
            confidence = probs[0, class_idx].item() * 100
        
        # CAM hesapla
        cam = self.generate_cam(input_tensor, class_idx, device)
        
        # Görselleştir
        overlay = self.overlay_cam_on_image(image, cam, alpha=0.4)
        
        return overlay, confidence


class SalienceMap:
    """
    Salience Map (Saliency Maps)
    Giriş görseline göre gradient hesaplayarak hangi piksellerin önemli olduğunu gösterir
    """
    
    def __init__(self):
        pass
    
    def generate(self, image_path, model, device='cuda'):
        """
        Salience map oluştur
        
        Args:
            image_path: Görsel dosyası yolu
            model: ResNet50 modeli
            device: 'cuda' veya 'cpu'
        
        Returns:
            saliency_map: (224, 224) NumPy array
        """
        from torchvision import transforms
        
        # Görsel yükle
        image = Image.open(image_path).convert('RGB')
        
        # Transform'ları uygula
        transform = transforms.Compose([
            transforms.Resize(int(224 * 1.15)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform(image).unsqueeze(0).to(device)
        input_tensor.requires_grad_(True)
        
        # Forward pass
        output = model(input_tensor)
        target_class = output.argmax(dim=1).item()
        target_score = output[0, target_class]
        
        # Backward pass
        model.zero_grad()
        target_score.backward()
        
        # Salience map hesapla (input gradientlerinin büyüklüğü)
        saliency = input_tensor.grad.data
        saliency = saliency.abs().max(dim=1)[0].squeeze()
        
        # Normalize et
        saliency_min = saliency.min()
        saliency_max = saliency.max()
        if saliency_max > saliency_min:
            saliency = (saliency - saliency_min) / (saliency_max - saliency_min)
        
        return saliency.cpu().numpy()


def image_to_base64(pil_image):
    """
    PIL Image'ı Base64 string'e dönüştür (JSON için)
    """
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"
