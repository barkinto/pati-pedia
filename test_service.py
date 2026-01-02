
from gemini_service import gemini_service
import os

print("Testing Gemini Service...")

if not gemini_service.is_configured():
    print("❌ API Key is missing! Check .env file.")
    exit(1)

print(f"✅ API Key found: {gemini_service.api_key[:5]}...")
print(f"✅ Using model: {gemini_service.model_name}")

print("\n--- Test 1: Simple Text Generation ---")
response = gemini_service.generate_content("Merhaba, sen kimsin? (Kısa cevap ver)")
if "text" in response:
    print(f"✅ Success: {response['text']}")
else:
    print(f"❌ Failed: {response['error']}")

print("\nTests completed.")
