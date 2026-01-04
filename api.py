"""
Flask RESTful API for Cat Breed Prediction
Backend API for React frontend
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms
import io
import base64
import os
import sys
import time
import json
import numpy as np
from functools import lru_cache
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except:
    YOLO_AVAILABLE = False

try:
    import requests
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

# Base directory for web application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend', 'dist')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)  # Enable CORS for React frontend

# Model paths
from huggingface_hub import hf_hub_download

# Model paths management
MODEL_REPO = "barkinto/kedi-modeli"
MODEL_FILENAME = "best.pth"

# Prioritize LOCAL model (Pre-deployment version)
MODEL_PATH = 'runs/resnet50_v2/weights/best.pth'

if os.path.exists(MODEL_PATH):
    print(f"✅ Yerel model (Deploy öncesi) bulundu ve kullanılıyor: {MODEL_PATH}")
else:
    print(f"⚠️ Yerel model bulunamadı: {MODEL_PATH}")
    print(f"🔄 Model dış kaynaktan indiriliyor: {MODEL_REPO}/{MODEL_FILENAME}...")
    try:
        # Download model from HF Hub (cache handled automatically)
        MODEL_PATH = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILENAME)
        print(f"✅ Model başarıyla indirildi: {MODEL_PATH}")
    except Exception as e:
        print(f"⚠️ Model indirme hatası: {e}")
        # Fallback to local check
        POSSIBLE_MODEL_PATHS = [
            'runs/resnet50/weights/best.pth',
            'best.pth',
            '/app/best.pth'
        ]
        MODEL_PATH = 'runs/resnet50_v2/weights/best.pth'  # Default fallback
    found_valid_model = False
    for path in POSSIBLE_MODEL_PATHS:
        if os.path.exists(path):
            # Check if file is larger than 1MB
            if os.path.getsize(path) > 1024 * 1024:
                MODEL_PATH = path
                found_valid_model = True
                print(f"✅ Yerel model bulundu: {MODEL_PATH}")
                break
YOLO_MODEL_PATH = 'yolo11n.pt'

# Global variables for loaded models
model = None
class_names = None
device = None
yolo_model = None

# Cache for Gemini API responses (breed name -> (response, timestamp))
gemini_cache = {}
CACHE_DURATION = 3600 * 24  # 24 hours cache

# Rate limiting for Gemini API (prevent too many requests)
last_api_call_time = defaultdict(float)
MIN_API_CALL_INTERVAL = 2.0  # Minimum 2 seconds between API calls


def load_models():
    """Load YOLO and ResNet50 models"""
    global model, class_names, device, yolo_model
    
    # Load YOLO model
    if YOLO_AVAILABLE:
        try:
            yolo_model = YOLO(YOLO_MODEL_PATH)
            print("✅ YOLO model loaded")
        except Exception as e:
            print(f"⚠️ YOLO model could not be loaded: {e}")
            yolo_model = None
    
    # Load ResNet50 model
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"📱 Using device: {device}")
        
        # Check if model file exists
        if not os.path.exists(MODEL_PATH):
            print(f"❌ Model file not found: {MODEL_PATH}")
            return False
        
        print(f"📂 Loading model from: {MODEL_PATH}")
        print(f"   File size: {os.path.getsize(MODEL_PATH) / (1024*1024):.2f} MB")
        
        # Try loading with different methods for compatibility
        try:
            checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
        except Exception as e1:
            print(f"⚠️ First load attempt failed: {e1}")
            try:
                # Try without weights_only for older PyTorch versions
                checkpoint = torch.load(MODEL_PATH, map_location=device)
            except Exception as e2:
                print(f"⚠️ Second load attempt failed: {e2}")
                # Try reading as binary first
                with open(MODEL_PATH, 'rb') as f:
                    checkpoint = torch.load(f, map_location=device)
        num_classes = len(checkpoint['class_names'])
        class_names = checkpoint['class_names']
        
        # Create model architecture
        model = models.resnet50(pretrained=False)
        num_ftrs = model.fc.in_features
        
        # Check if checkpoint uses Sequential (with dropout) or simple Linear
        state_dict = checkpoint['model_state_dict']
        if 'fc.weight' in state_dict:
            # Simple Linear layer
            print("ℹ️ Model yapısı: Simple Linear (fc.weight bulundu)")
            model.fc = nn.Linear(num_ftrs, num_classes)
        else:
            # Sequential (Dropout + Linear)
            print("ℹ️ Model yapısı: Sequential (fc.1.weight bekleniyor)")
            model.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_ftrs, num_classes)
            )
        model.load_state_dict(checkpoint['model_state_dict'])
        model = model.to(device)
        model.eval()
        
        print(f"✅ ResNet50 model loaded ({num_classes} classes)")
        return True
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False


def detect_cat(image, yolo_model):
    """Detect if image contains a cat using YOLO"""
    if yolo_model is None:
        return True, 1.0, "YOLO mevcut değil - tespit atlanıyor"
    
    try:
        results = yolo_model(image, verbose=False)
        
        if len(results) == 0:
            return False, 0.0, "Hiçbir nesne tespit edilemedi"
        
        cat_found = False
        max_cat_conf = 0.0
        
        for result in results:
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue
            
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Class 15 = cat in COCO dataset
                if cls == 15 and conf > 0.15:
                    cat_found = True
                    max_cat_conf = max(max_cat_conf, conf)
        
        if cat_found:
            return True, max_cat_conf, f"Kedi tespit edildi (güven: {max_cat_conf:.2f})"
        
        return False, 0.0, "Bu görselde kedi tespit edilemedi"
    except Exception as e:
        return True, 1.0, f"Tespit hatası: {str(e)[:100]}"


def preprocess_image(image):
    """Preprocess image for ResNet-50"""
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    image_tensor = transform(image).unsqueeze(0)
    return image_tensor


def predict_breed(image, top_k=5, uncertainty_threshold=0.9):
    """Predict cat breed with top-k results and entropy-based wild cat detection
    
    Args:
        image: PIL Image
        top_k: Number of top predictions to return
        uncertainty_threshold: Entropy threshold for wild cat detection (default: 0.9)
                              Higher values = more conservative detection
                              Lower values = more aggressive detection
    
    Returns:
        tuple: (results, entropy, is_wild_cat)
            - results: List of predictions with breed and confidence
            - entropy: Prediction entropy (uncertainty metric)
            - is_wild_cat: Boolean indicating if this is likely a wild cat
    """
    global model, class_names, device
    
    if model is None or class_names is None:
        return None, None, None
    
    try:
        # Preprocess
        image_tensor = preprocess_image(image)
        image_tensor = image_tensor.to(device)
        
        # Predict
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            top_probs, top_indices = torch.topk(probabilities, top_k)
        
        # Calculate prediction entropy (uncertainty)
        # High entropy = predictions spread out (wild cat, uncertain)
        # Low entropy = one prediction dominates (domestic cat, confident)
        top_probs_np = top_probs[0].cpu().numpy()
        entropy = -np.sum(top_probs_np * np.log(top_probs_np + 1e-10))
        
        # Convert numpy types to native Python types for JSON serialization
        entropy = float(entropy)
        
        # Detect wild cats based on entropy
        # Domestic cats: Low entropy (~0.3-0.8) - one prediction dominates
        # Wild cats: High entropy (~0.9-2.0) - predictions spread out
        is_wild_cat = bool(entropy > uncertainty_threshold)
        
        # Format results with native Python types
        results = []
        for prob, idx in zip(top_probs[0], top_indices[0]):
            results.append({
                'breed': str(class_names[int(idx)]),
                'confidence': float(round(prob.item() * 100, 2))
            })
        
        return results, round(entropy, 4), is_wild_cat
    except Exception as e:
        print(f"Error in prediction: {e}")
        return None, None, None


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'yolo_loaded': yolo_model is not None,
        'device': str(device) if device else None,
        'num_classes': len(class_names) if class_names else 0
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict cat breed from uploaded image"""
    try:
        # Check if image is in request
        if 'image' not in request.files:
            return jsonify({'error': 'Görsel dosyası sağlanmadı'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Görsel dosyası seçilmedi'}), 400
        
        # Read image with format validation
        try:
            image_bytes = file.read()
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert all formats to RGB (RGBA, P, L, CMYK, etc.)
            if image.mode not in ['RGB']:
                image = image.convert('RGB')
                
        except Exception as e:
            return jsonify({'error': f'Görsel dosyası açılamadı: {str(e)}'}), 400
        
        # Optional: skip detection flag
        skip_detection = request.form.get('skip_detection', 'false').lower() == 'true'
        
        # Detect cat (optional)
        cat_detected = True
        cat_confidence = 1.0
        detection_message = "Tespit atlandı"
        
        if not skip_detection:
            cat_detected, cat_confidence, detection_message = detect_cat(image, yolo_model)
        
        if not cat_detected:
            return jsonify({
                'error': 'Bu görselde kedi tespit edilemedi',
                'detection_message': detection_message,
                'cat_detected': False
            }), 400
        
        # Get uncertainty threshold from request (optional)
        uncertainty_threshold = float(request.form.get('uncertainty_threshold', '0.9'))
        
        # Predict breed with entropy-based wild cat detection
        results, entropy, is_wild_cat = predict_breed(image, top_k=5, uncertainty_threshold=uncertainty_threshold)
        
        if results is None:
            return jsonify({'error': 'Tahmin başarısız oldu'}), 500
        
        # Convert image to base64 for Gemini Vision analysis
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Analyze cat image with Gemini Vision (optional - skip if quota exceeded)
        cat_analysis = None
        cat_analysis_error = None
        if GEMINI_AVAILABLE and results:
            try:
                top_breed = results[0]['breed'] if results else None
                print(f"🔍 Görsel analizi başlatılıyor (Cins: {top_breed})...")
                cat_analysis = analyze_cat_image_with_gemini(image_base64, top_breed)
                
                # Check if it's a quota error message or special marker
                if cat_analysis == "QUOTA_ERROR":
                    print("⚠️ Görsel analizi quota hatası (QUOTA_ERROR) - uyarı mesajı gönderiliyor")
                    cat_analysis = None
                    cat_analysis_error = "⚠️ API quota limiti aşıldı. Görsel analiz özelliği şu anda kullanılamıyor. Tahmin özelliği normal çalışmaya devam ediyor."
                elif cat_analysis and isinstance(cat_analysis, str) and ("quota" in cat_analysis.lower() or "⚠️" in cat_analysis or "limit" in cat_analysis.lower() or "429" in str(cat_analysis)):
                    print("⚠️ Görsel analizi quota hatası (string içinde) - uyarı mesajı gönderiliyor")
                    cat_analysis = None
                    cat_analysis_error = "⚠️ API quota limiti aşıldı. Görsel analiz özelliği şu anda kullanılamıyor. Tahmin özelliği normal çalışmaya devam ediyor."
                elif cat_analysis:
                    print(f"✅ Görsel analizi tamamlandı ({len(cat_analysis)} karakter)")
                else:
                    # cat_analysis None ise, bu quota hatası veya başka bir hata olabilir
                    print("⚠️ Görsel analizi sonuç döndürmedi (None) - uyarı mesajı gönderiliyor")
                    cat_analysis_error = "⚠️ Görsel analiz şu anda kullanılamıyor. Tahmin özelliği normal çalışmaya devam ediyor."
            except Exception as e:
                print(f"⚠️ Görsel analizi hatası (opsiyonel): {e}")
                cat_analysis = None
                cat_analysis_error = "⚠️ Görsel analiz şu anda kullanılamıyor. Tahmin özelliği normal çalışmaya devam ediyor."
        else:
            # GEMINI_AVAILABLE değilse veya results yoksa
            if results:
                cat_analysis_error = "⚠️ Görsel analiz şu anda kullanılamıyor. Tahmin özelliği normal çalışmaya devam ediyor."
        
        response_data = {
            'success': True,
            'predictions': results,
            'entropy': entropy,
            'is_wild_cat': is_wild_cat,
            'uncertainty_threshold': uncertainty_threshold,
            'cat_detection': {
                'detected': cat_detected,
                'confidence': round(cat_confidence * 100, 2),
                'message': detection_message
            },
            'wild_cat_info': {
                'detected': is_wild_cat,
                'entropy': entropy,
                'threshold': uncertainty_threshold,
                'explanation': (
                    "🦁 VAHŞİ KEDİ TESPİT EDİLDİ! Bu kedi türü veri setinde yok. "
                    "Model 59 ev kedisi ırkı için eğitildi. Muhtemel sebepler: "
                    "Vahşi kedi (vaşak, puma, kaplan vb.), Hibrit tür, Çok kötü fotoğraf kalitesi"
                ) if is_wild_cat else (
                    "✅ Ev kedisi tespit edildi. Tahmin güvenilir."
                )
            }
        }
        
        if cat_analysis:
            response_data['cat_analysis'] = cat_analysis
        
        if cat_analysis_error:
            response_data['cat_analysis_error'] = cat_analysis_error
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/classes', methods=['GET'])
def get_classes():
    """Get list of all cat breed classes"""
    if class_names is None:
        return jsonify({'error': 'Model yüklenmedi'}), 500
    
    return jsonify({
        'classes': class_names,
        'total': len(class_names)
    })


# Load static breed info database
BREED_INFO_DB = None
BREED_INFO_DB_PATH = os.path.join(BASE_DIR, 'cat_breed_info.json')

def load_breed_info_db():
    """Load static breed information database"""
    global BREED_INFO_DB
    if BREED_INFO_DB is None:
        try:
            if os.path.exists(BREED_INFO_DB_PATH):
                with open(BREED_INFO_DB_PATH, 'r', encoding='utf-8') as f:
                    BREED_INFO_DB = json.load(f)
                print(f"✅ Statik kedi cinsi bilgi veritabanı yüklendi ({len(BREED_INFO_DB)} cins)")
            else:
                print(f"⚠️ Kedi cinsi bilgi dosyası bulunamadı: {BREED_INFO_DB_PATH}")
                BREED_INFO_DB = {}
        except Exception as e:
            print(f"❌ Kedi cinsi bilgi veritabanı yüklenirken hata: {e}")
            BREED_INFO_DB = {}
    return BREED_INFO_DB

def get_breed_info_from_static_db(breed_name):
    """Get cat breed information from static database (FREE, no API needed)"""
    db = load_breed_info_db()
    
    # Try exact match first
    if breed_name in db:
        info = db[breed_name]
        result = f"""**Karakter:** {info.get('karakter', 'Bilgi bulunamadı')}

**Bakım:** {info.get('bakim', 'Bilgi bulunamadı')}

**Sağlık:** {info.get('saglik', 'Bilgi bulunamadı')}

**Mama:** {info.get('mama', 'Bilgi bulunamadı')}

**Yaşam:** {info.get('yasam', 'Bilgi bulunamadı')}"""
        print(f"✅ Statik veritabanından alındı: {breed_name}")
        return result
    
    # Try case-insensitive match
    breed_lower = breed_name.lower()
    for key, value in db.items():
        if key.lower() == breed_lower:
            info = value
            result = f"""**Karakter:** {info.get('karakter', 'Bilgi bulunamadı')}

**Bakım:** {info.get('bakim', 'Bilgi bulunamadı')}

**Sağlık:** {info.get('saglik', 'Bilgi bulunamadı')}

**Mama:** {info.get('mama', 'Bilgi bulunamadı')}

**Yaşam:** {info.get('yasam', 'Bilgi bulunamadı')}"""
            print(f"✅ Statik veritabanından alındı (case-insensitive): {breed_name}")
            return result
    
    print(f"⚠️ {breed_name} için statik veritabanında bilgi bulunamadı")
    return None

def get_breed_info_from_gemini(breed_name):
    """Get cat breed information from Gemini AI using REST API with caching and rate limiting (FALLBACK - requires API key)"""
    # First try static database (FREE)
    static_info = get_breed_info_from_static_db(breed_name)
    if static_info:
        return static_info
    
    # If not found in static DB, try Gemini API (if available and configured)
    if not GEMINI_AVAILABLE:
        return None
    
    # Normalize breed name for cache key
    cache_key = breed_name.lower().strip()
    
    # Check cache first (24 hour cache)
    current_time = time.time()
    if cache_key in gemini_cache:
        cached_response, cached_time = gemini_cache[cache_key]
        if current_time - cached_time < CACHE_DURATION:
            print(f"✅ Cache'den döndürüldü: {breed_name}")
            return cached_response
        else:
            # Cache expired, remove it
            del gemini_cache[cache_key]
    
    # Rate limiting: Check if we need to wait
    time_since_last_call = current_time - last_api_call_time['breed_info']
    if time_since_last_call < MIN_API_CALL_INTERVAL:
        wait_time = MIN_API_CALL_INTERVAL - time_since_last_call
        print(f"⏳ Rate limiting: {wait_time:.1f} saniye bekleniyor...")
        time.sleep(wait_time)
    
    try:
        # Get API key from environment variable or use default
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyD919v-LWT423ZpSX1MHPcjnlNsVuQW7PQ')
        if not api_key:
            print("⚠️ GEMINI_API_KEY environment variable not set")
            # HARD DEBUG: Check all env vars
            print("🔎 DEBUG - Environment keys:", list(os.environ.keys()))
            return None
        
        # Debug: Print loaded key (masked)
        masked_key = f"{api_key[:5]}...{api_key[-4:]}" if api_key and len(api_key) > 10 else "INVALID"
        print(f"🔑 DEBUG: Loaded GEMINI_API_KEY: {masked_key}")
        
        # Update last call time
        last_api_call_time['breed_info'] = time.time()
        
        # Create prompt
        prompt = f"""Lütfen {breed_name} kedi cinsi hakkında kedi sahipleri için pratik ve kısa bilgiler ver. 
Aşağıdaki bilgileri Türkçe olarak, kısa ve öz şekilde ver (her bölüm 2-3 cümle):
1. **Karakter:** Bu kedi nasıl bir karaktere sahip? (sakin/aktif, sosyal/bağımsız, çocuklarla uyumlu mu?)
2. **Bakım:** Günlük bakımda nelere dikkat edilmeli? (tüy bakımı, egzersiz ihtiyacı)
3. **Sağlık:** Bilinen sağlık sorunları neler? (dikkat edilmesi gerekenler)
4. **Mama:** Bu cins için önerilen mama markaları ve beslenme ipuçları (kuru/yaş mama önerileri)
5. **Yaşam:** Hangi ortamlarda mutlu olur? (apartman/ev, çocuklu aile, tek kişi)

Toplam maksimum 200 kelime. Pratik ve kedi sahipleri için faydalı bilgiler ver."""

        # Call Gemini REST API
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': api_key
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 429:
            print("⚠️ Gemini API quota aşıldı (429). Statik veritabanı kullanılıyor.")
            return None
        elif response.status_code == 401 or response.status_code == 403:
            print("⚠️ Gemini API yetkilendirme hatası. Statik veritabanı kullanılıyor.")
            return None
        
        response.raise_for_status()
        
        result = response.json()
        
        # Extract text from response
        if 'candidates' in result and len(result['candidates']) > 0:
            if 'content' in result['candidates'][0]:
                if 'parts' in result['candidates'][0]['content']:
                    if len(result['candidates'][0]['content']['parts']) > 0:
                        response_text = result['candidates'][0]['content']['parts'][0].get('text', '')
                        # Cache the successful response
                        if response_text:
                            gemini_cache[cache_key] = (response_text, time.time())
                            print(f"✅ Gemini API'den alındı ve cache'lendi: {breed_name}")
                        return response_text
        
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401 or e.response.status_code == 403:
            print("⚠️ Gemini API yetkilendirme hatası. Statik veritabanı kullanılıyor.")
            return None
        elif e.response.status_code == 429:
            print("⚠️ Gemini API quota hatası. Statik veritabanı kullanılıyor.")
            return None
        else:
            print(f"⚠️ Gemini AI HTTP error: {e.response.status_code}. Statik veritabanı kullanılıyor.")
            return None
    except Exception as e:
        print(f"⚠️ Gemini AI error: {e}. Statik veritabanı kullanılıyor.")
        return None


@app.route('/api/breed-info', methods=['POST'])
def get_breed_info():
    """Get cat breed information from Gemini AI"""
    try:
        data = request.get_json()
        breed_name = data.get('breed')
        
        if not breed_name:
            return jsonify({'error': 'Kedi cinsi adı sağlanmadı'}), 400
        
        info = get_breed_info_from_gemini(breed_name)
        
        # Statik veritabanı kullanılıyor, hata mesajı döndürmeye gerek yok
        if info is None:
            return jsonify({
                'error': f'{breed_name} cinsi için bilgi bulunamadı. Statik veritabanında henüz eklenmemiş olabilir.',
                'breed': breed_name,
                'success': False
            }), 404
        
        # Check if info is an error message (quota, API key, etc.) - should not happen with static DB
        if isinstance(info, str) and ('quota' in info.lower() or '⚠️' in info or 'error' in info.lower() or 'API key' in info or 'geçersiz' in info.lower() or 'limit' in info.lower()):
            # If it's an error, return None (static DB will be used)
            return jsonify({
                'error': f'{breed_name} cinsi için bilgi bulunamadı.',
                'breed': breed_name,
                'success': False
            }), 404
        
        return jsonify({
            'success': True,
            'breed': breed_name,
            'info': info
        })
        
    except Exception as e:
        return jsonify({'error': f'Hata: {str(e)}'}), 500


def analyze_cat_image_with_gemini(image_base64, breed_name=None):
    """Analyze cat image using Gemini AI vision model with rate limiting"""
    if not GEMINI_AVAILABLE:
        return None
    
    # Rate limiting: Check if we need to wait
    current_time = time.time()
    time_since_last_call = current_time - last_api_call_time['image_analysis']
    if time_since_last_call < MIN_API_CALL_INTERVAL:
        wait_time = MIN_API_CALL_INTERVAL - time_since_last_call
        print(f"⏳ Rate limiting: {wait_time:.1f} saniye bekleniyor...")
        time.sleep(wait_time)
    
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        
        # Debug: Print loaded key status (masked)
        if api_key:
            masked_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 10 else "SHORT_KEY"
            print(f"🔑 DEBUG (Vision): Loaded GEMINI_API_KEY: {masked_key}")
        else:
            print("❌ DEBUG (Vision): GEMINI_API_KEY bulunamadı (Environment variable boş)")
            print("🔎 DEBUG (Vision) - Env keys:", list(os.environ.keys()))
            
        if not api_key:
            return None
        
        # Update last call time
        last_api_call_time['image_analysis'] = time.time()
        
        # Create prompt for image analysis
        breed_context = f" Tahmin edilen cins: {breed_name}." if breed_name else ""
        prompt = f"""Bu kedi fotoğrafını analiz et ve aşağıdaki bilgileri Türkçe olarak, kısa ve pratik şekilde ver:

**1. Yaş Tahmini:** Yavru mu, genç mi (1-2 yaş), yetişkin mi (3-7 yaş), yaşlı mı (8+ yaş)? Gözler, vücut yapısı ve tüy durumuna bakarak tahmin et.

**2. Sağlık Durumu:** Genel görünümü sağlıklı görünüyor mu? Tüy kalitesi, göz parlaklığı, vücut kondisyonu (zayıf/normal/kilolu) nasıl?

**3. Fiziksel Özellikler:** Vücut yapısı, tüy durumu, genel görünüm hakkında kısa notlar.

**4. Bakım Önerileri:** Bu kedinin görünümüne göre özel bakım önerileri (varsa).

{breed_context}

Her bölüm 1-2 cümle, toplam maksimum 150 kelime."""

        # Prepare image data
        # Remove data URL prefix if present
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        # Call Gemini Vision API
        # Use gemini-1.5-flash (same as text generation)
        # Clean API Key (remove spaces/newlines)
        api_key = api_key.strip()
        if not api_key:
             return None

        # Call Gemini Vision API
        # Use simple URL with query param as backup
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        headers = {
            'Content-Type': 'application/json'
            # 'X-goog-api-key': api_key # Query param is enough and safer
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 429:
            error_msg = response.json().get('error', {}).get('message', 'Quota aşıldı')
            print(f"⚠️ Gemini API quota aşıldı (429): {error_msg}")
            return "QUOTA_ERROR"  # Return special marker so parent function can set error message
        
        response.raise_for_status()
        
        result = response.json()
        
        # Extract text from response
        if 'candidates' in result and len(result['candidates']) > 0:
            if 'content' in result['candidates'][0]:
                if 'parts' in result['candidates'][0]['content']:
                    if len(result['candidates'][0]['content']['parts']) > 0:
                        return result['candidates'][0]['content']['parts'][0].get('text', '')
        
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("⚠️ Gemini API quota aşıldı (429). Görsel analizi atlanıyor.")
            return "QUOTA_ERROR"  # Special marker for quota error
        elif e.response.status_code == 401 or e.response.status_code == 403:
            error_msg = "API key geçersiz veya süresi dolmuş. Lütfen yeni bir API key oluşturun."
            print(f"❌ Gemini API yetkilendirme hatası ({e.response.status_code}): {error_msg}")
            return None
        else:
            print(f"❌ Gemini Vision API HTTP error: {e.response.status_code} - {e.response.text[:200]}")
        return None
    except Exception as e:
        print(f"❌ Gemini Vision AI error: {e}")
        return None


@app.route('/api/analyze-cat', methods=['POST'])
def analyze_cat():
    """Analyze cat image for health, age, and other characteristics"""
    try:
        # Check if image is in request
        if 'image' not in request.files:
            # Try to get base64 image from JSON
            data = request.get_json()
            if data and 'image_base64' in data:
                image_base64 = data['image_base64']
                breed_name = data.get('breed', None)
            else:
                return jsonify({'error': 'Görsel dosyası veya base64 görsel sağlanmadı'}), 400
        else:
            # Get image from file upload
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'Görsel dosyası seçilmedi'}), 400
            
            # Read and convert to base64
            image = Image.open(io.BytesIO(file.read()))
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            breed_name = request.form.get('breed', None)
        
        # Analyze with Gemini Vision
        analysis = analyze_cat_image_with_gemini(image_base64, breed_name)
        
        if analysis is None:
            return jsonify({
                'error': 'Görsel analizi yapılamadı. Gemini AI kontrol edin.',
            }), 500
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'breed': breed_name
        })
        
    except Exception as e:
        return jsonify({'error': f'Hata: {str(e)}'}), 500


# Serve frontend static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve React frontend"""
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    else:
        # Serve index.html for React Router
        index_path = os.path.join(FRONTEND_DIR, 'index.html')
        if os.path.exists(index_path):
            return send_file(index_path)
        else:
            return jsonify({'error': 'Frontend build not found. Please build frontend first.'}), 404


if __name__ == '__main__':
    import traceback
    try:
        print("🚀 Starting Flask API server...")
        print(f"📁 BASE_DIR: {BASE_DIR}")
        print(f"📁 MODEL_PATH: {MODEL_PATH}")
        print(f"📁 YOLO_MODEL_PATH: {YOLO_MODEL_PATH}")
        print(f"📁 FRONTEND_DIR: {FRONTEND_DIR}")
        
        # Check if files exist
        print(f"📂 Checking files...")
        print(f"   MODEL_PATH exists: {os.path.exists(MODEL_PATH)}")
        print(f"   YOLO_MODEL_PATH exists: {os.path.exists(YOLO_MODEL_PATH)}")
        print(f"   FRONTEND_DIR exists: {os.path.exists(FRONTEND_DIR)}")
        
        if not os.path.exists(MODEL_PATH):
            print(f"❌ Model file not found: {MODEL_PATH}")
            print(f"   Current working directory: {os.getcwd()}")
        
        print("📦 Loading models...")
        
        if load_models():
            print("✅ All models loaded successfully!")
            print("🌐 Starting server on http://localhost:5001")
            print("📡 API endpoints:")
            print("   - GET  /api/health")
            print("   - POST /api/predict")
            print("   - GET  /api/classes")
            print("   - POST /api/breed-info (Gemini AI - Kedi cinsi bilgisi)")
            print("   - POST /api/analyze-cat (Gemini Vision - Fotoğraf analizi)")
            if GEMINI_AVAILABLE:
                print("   ✅ Gemini AI hazır (GEMINI_API_KEY gerekli)")
            else:
                print("   ⚠️  Gemini AI yüklü değil")
            
            app.run(host='0.0.0.0', port=5001, debug=False)
        else:
            print("❌ Failed to load models. Exiting...")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        sys.exit(1)

