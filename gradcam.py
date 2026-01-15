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


class GuidedBackpropagation:
    """
    Guided Backpropagation
    ReLU katmanlarında sadece pozitif gradyanları geri yayarak
    net kenar çizgileri elde eder.
    """
    
    def __init__(self, model):
        self.model = model
        self.gradients = None
        self.forward_relu_outputs = []
        self.hooks = []
        
        # Model'daki tüm ReLU'ları bul ve hook ekle
        self._register_hooks()
    
    def _register_hooks(self):
        """ReLU katmanlarına hook ekle"""
        def relu_backward_hook(module, grad_input, grad_output):
            # Guided: sadece pozitif gradyanları geri yay
            # ve sadece forward'da pozitif olan yerleri al
            if len(self.forward_relu_outputs) > 0:
                forward_output = self.forward_relu_outputs.pop()
                # Hem gradyan pozitif hem de forward çıktı pozitif olmalı
                guided_grad = torch.clamp(grad_input[0], min=0.0)
                guided_grad = guided_grad * (forward_output > 0).float()
                return (guided_grad,)
            return grad_input
        
        def relu_forward_hook(module, input, output):
            self.forward_relu_outputs.append(output)
        
        # Model'daki tüm ReLU modüllerini bul
        for module in self.model.modules():
            if isinstance(module, torch.nn.ReLU):
                self.hooks.append(module.register_forward_hook(relu_forward_hook))
                self.hooks.append(module.register_full_backward_hook(relu_backward_hook))
    
    def generate(self, input_tensor, target_class=None):
        """
        Guided Backpropagation haritası oluştur
        
        Returns:
            guided_grads: (H, W) numpy array - kenar haritası
        """
        self.forward_relu_outputs = []
        
        # ReLU inplace'i devre dışı bırak (backward hook ile çakışıyor)
        relu_inplace_states = []
        for module in self.model.modules():
            if isinstance(module, torch.nn.ReLU):
                relu_inplace_states.append(module.inplace)
                module.inplace = False
        
        try:
            # Gradient takibi aç
            input_tensor = input_tensor.clone().detach().requires_grad_(True)
            
            # Forward pass
            output = self.model(input_tensor)
            
            if target_class is None:
                target_class = output.argmax(dim=1).item()
            
            # Backward pass
            self.model.zero_grad()
            target_score = output[0, target_class]
            target_score.backward()
            
            # Gradyanları al
            gradients = input_tensor.grad.data[0]  # (3, H, W)
            
            # RGB kanallarının maksimumunu al
            guided_grads = gradients.abs().max(dim=0)[0]  # (H, W)
            
            return guided_grads.cpu().numpy()
        finally:
            # ReLU inplace'i eski haline getir
            i = 0
            for module in self.model.modules():
                if isinstance(module, torch.nn.ReLU):
                    module.inplace = relu_inplace_states[i]
                    i += 1
    
    def visualize(self, guided_grads, colormap='gray'):
        """
        Guided Backprop sonucunu görselleştir
        """
        # Normalize
        grads = guided_grads.copy()
        grads = grads - grads.min()
        grads = grads / (grads.max() + 1e-8)
        
        # 0-255 aralığına çek
        grads = (grads * 255).astype(np.uint8)
        
        if colormap == 'gray':
            # Siyah-beyaz (kenar görünümü)
            return Image.fromarray(grads)
        else:
            # Renkli versiyon
            colored = cv2.applyColorMap(grads, cv2.COLORMAP_VIRIDIS)
            colored = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
            return Image.fromarray(colored)
    
    def remove_hooks(self):
        """Hook'ları temizle"""
        for hook in self.hooks:
            hook.remove()
        self.hooks = []


class GuidedGradCAM:
    """
    Guided Grad-CAM
    Grad-CAM (bölgesel) + Guided Backprop (piksel detayı) birleşimi
    En profesyonel XAI görselleştirmesi
    """
    
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self._guided_bp = None
    
    def generate(self, input_tensor, target_class=None):
        """
        Guided Grad-CAM haritası oluştur
        
        Returns:
            guided_gradcam: (H, W) numpy array
        """
        # Tahmin sınıfı
        with torch.no_grad():
            output = self.model(input_tensor)
            if target_class is None:
                target_class = output.argmax(dim=1).item()
        
        # 1. Grad-CAM hesapla (bölgesel harita) - ÖNCE bunu yap, hook yok
        gradcam = GradCAM(self.model, self.target_layer)
        cam = gradcam.generate_cam(input_tensor.clone(), target_class)
        
        # 2. Guided Backprop hesapla (kenar haritası) - SONRA hook ekle
        self._guided_bp = GuidedBackpropagation(self.model)
        guided = self._guided_bp.generate(input_tensor.clone(), target_class)
        
        # 3. CAM'i guided boyutuna resize et
        cam_resized = cv2.resize(cam, (guided.shape[1], guided.shape[0]))
        
        # 4. Element-wise çarpım (Guided Grad-CAM)
        guided_gradcam = cam_resized * guided
        
        return guided_gradcam
    
    def visualize(self, guided_gradcam, original_image=None, alpha=0.5):
        """
        Guided Grad-CAM sonucunu görselleştir
        """
        # Normalize
        ggc = guided_gradcam.copy()
        ggc = ggc - ggc.min()
        ggc = ggc / (ggc.max() + 1e-8)
        
        # 0-255 aralığına çek
        ggc = (ggc * 255).astype(np.uint8)
        
        # Renkli heatmap
        heatmap = cv2.applyColorMap(ggc, cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        if original_image is not None:
            # Orijinal ile overlay
            if isinstance(original_image, Image.Image):
                orig = np.array(original_image)
            else:
                orig = original_image
            
            # Resize heatmap to original size
            heatmap = cv2.resize(heatmap, (orig.shape[1], orig.shape[0]))
            
            # Blend
            overlay = cv2.addWeighted(orig, 1 - alpha, heatmap, alpha, 0)
            return Image.fromarray(overlay)
        
        return Image.fromarray(heatmap)
    
    def cleanup(self):
        """Hook'ları temizle"""
        if self._guided_bp:
            self._guided_bp.remove_hooks()


# SmoothGrad Saliency Map (Akademik Standart)
class SalienceMap:
    """
    SmoothGrad Tabanlı Saliency Map
    
    Vanilla Saliency yerine SmoothGrad kullanarak gürültüyü azaltır.
    Grad-CAM odak bölgesi ile sınırlandırılabilir.
    
    Referans: Smilkov et al. (2017) "SmoothGrad: removing noise by adding noise"
    
    Akademik İyileştirmeler:
    - SmoothGrad: n=30 gürültülü örnek üzerinden ortalama
    - ReLU aktivasyonu: Negatif gradyanları filtrele (Grad-CAM uyumu)
    - Grad-CAM maskeleme: Odak bölgesi dışını filtrele
    - Sobel kenar farkındalığı: Anatomik detayları vurgula
    - Z-score normalizasyonu: Akademik standart
    """
    
    def __init__(self, n_samples=30, noise_std=0.1):
        """
        Args:
            n_samples: SmoothGrad için örnek sayısı (30 = akademik standart)
            noise_std: Gürültü standart sapması (0.1 = optimal)
        """
        self.n_samples = n_samples
        self.noise_std = noise_std
    
    def generate_saliency(self, input_tensor, model, device='cuda', target_class=None, gradcam_mask=None):
        """
        SmoothGrad Saliency Map oluştur
        
        Args:
            input_tensor: İşlenmiş görsel tensorü (1, 3, 224, 224)
            model: ResNet50 modeli
            device: 'cuda' veya 'cpu'
            target_class: Hedef sınıf indeksi (None ise tahmin edilen sınıf kullanılır)
            gradcam_mask: Opsiyonel Grad-CAM haritası (saliency'yi bölgeyle sınırla)
        
        Returns:
            saliency_map: (224, 224) tensor
        """
        # Hedef sınıfı belirle (dışarıdan verilmediyse ilk forward'dan al)
        if target_class is None:
            with torch.no_grad():
                output = model(input_tensor)
                target_class = output.argmax(dim=1).item()
        
        saliency_sum = None
        
        for _ in range(self.n_samples):
            # Gürültü ekle
            noise = torch.randn_like(input_tensor) * self.noise_std
            noisy_input = (input_tensor + noise).clone().detach().requires_grad_(True)
            
            # Forward pass
            output = model(noisy_input)
            target_score = output[0, target_class]
            
            # Backward pass
            model.zero_grad()
            target_score.backward()
            
            # Saliency = gradient MEAN across channels + ReLU (Grad-CAM uyumu)
            saliency = noisy_input.grad.data.mean(dim=1).squeeze()
            saliency = torch.relu(saliency)  # Sadece pozitif etkiler
            
            if saliency_sum is None:
                saliency_sum = saliency
            else:
                saliency_sum = saliency_sum + saliency
        
        # Ortalama al
        smooth_saliency = saliency_sum / self.n_samples
        
        # Grad-CAM maskesi ile sınırla (opsiyonel)
        if gradcam_mask is not None:
            if isinstance(gradcam_mask, np.ndarray):
                gradcam_mask = torch.from_numpy(gradcam_mask).to(smooth_saliency.device)
            # Resize mask to saliency size
            if gradcam_mask.shape != smooth_saliency.shape:
                gradcam_mask = F.interpolate(
                    gradcam_mask.unsqueeze(0).unsqueeze(0).float(),
                    size=smooth_saliency.shape,
                    mode='bilinear',
                    align_corners=False
                ).squeeze()
            smooth_saliency = smooth_saliency * gradcam_mask
        
        return smooth_saliency
    
    def _apply_sobel_edges(self, saliency_np, original_image):
        """
        Sobel kenar tespiti ile saliency'yi anatomik detaylara odakla
        """
        # Orijinal görseli grayscale'e çevir
        if isinstance(original_image, Image.Image):
            img_gray = np.array(original_image.convert('L'))
        else:
            img_gray = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
        
        # Resize to saliency size
        img_gray = cv2.resize(img_gray, (saliency_np.shape[1], saliency_np.shape[0]))
        
        # Sobel kenar tespiti
        sobelx = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_edges = np.sqrt(sobelx**2 + sobely**2)
        
        # Normalize edges
        sobel_edges = (sobel_edges - sobel_edges.min()) / (sobel_edges.max() - sobel_edges.min() + 1e-8)
        
        # Kenarları vurgula (ama tamamen bastırma)
        edge_weight = 0.5 + 0.5 * sobel_edges
        return saliency_np * edge_weight

    def visualize_saliency(self, saliency_map, original_image=None, use_edges=True):
        """
        Saliency map'i görselleştir (Akademik standart)
        
        Args:
            saliency_map: Saliency tensor veya numpy array
            original_image: Orijinal PIL Image (kenar tespiti için)
            use_edges: Sobel kenar farkındalığı kullan
        """
        if isinstance(saliency_map, torch.Tensor):
            saliency_map = saliency_map.cpu().numpy()
        
        # Sobel kenar farkındalığı ekle
        if use_edges and original_image is not None:
            saliency_map = self._apply_sobel_edges(saliency_map, original_image)
        
        # Z-score normalization (akademik standart)
        mean_val = saliency_map.mean()
        std_val = saliency_map.std()
        saliency_map = (saliency_map - mean_val) / (std_val + 1e-8)
        saliency_map = np.clip(saliency_map, 0, 3)  # 0-3σ aralığı
        saliency_map = saliency_map / 3.0  # 0-1 normalize
        
        # Hafif blur (gürültü temizleme)
        saliency_map = cv2.GaussianBlur(saliency_map.astype(np.float32), (5, 5), 0)
        
        # 0-255
        smap = (saliency_map * 255).astype(np.uint8)
        
        # JET colormap (kırmızı = yüksek, mavi = düşük)
        colored = cv2.applyColorMap(smap, cv2.COLORMAP_JET)
        colored = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
        
        return Image.fromarray(colored)


def image_to_base64(pil_image):
    """
    PIL Image'ı Base64 string'e dönüştür (JSON için)
    """
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"
