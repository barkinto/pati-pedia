
import os
import time
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        # Use gemini-flash-latest (Stable alias)
        self.model_name = "gemini-flash-latest" 
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
    def is_configured(self):
        return bool(self.api_key)

    def _get_headers(self):
        return {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }

    def generate_content(self, prompt):
        if not self.api_key:
            return {"error": "API Key eksik"}

        url = f"{self.base_url}/{self.model_name}:generateContent"
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        try:
            response = requests.post(url, headers=self._get_headers(), json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    return {"text": result['candidates'][0]['content']['parts'][0]['text']}
                return {"error": "Boş yanıt döndü"}
            
            return {"error": f"API Hatası: {response.status_code} - {response.text}"}
            
        except Exception as e:
            return {"error": f"Bağlantı hatası: {str(e)}"}

    def analyze_image(self, image_base64, prompt):
        if not self.api_key:
            return {"error": "API Key eksik"}

        # Handle data URL prefix if present
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]

        url = f"{self.base_url}/{self.model_name}:generateContent"
        
        data = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }]
        }

        try:
            response = requests.post(url, headers=self._get_headers(), json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    return {"text": result['candidates'][0]['content']['parts'][0]['text']}
                return {"error": "Boş yanıt döndü"}
                
            return {"error": f"API Hatası: {response.status_code} - {response.text}"}
            
        except Exception as e:
            return {"error": f"Bağlantı hatası: {str(e)}"}

# Singleton instance
gemini_service = GeminiService()
