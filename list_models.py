
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    models = response.json().get('models', [])
    print("Available models:")
    for model in models:
        print(f"- {model['name']} (Supported methods: {model.get('supportedGenerationMethods')})")
else:
    print(f"Error listing models: {response.status_code}")
    print(response.text)
