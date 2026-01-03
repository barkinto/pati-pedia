"""
PatiPedia - Kedi Cinsi Tanıma ve Bilgi Platformu
Hugging Face Spaces Deployment
"""

import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import api

# Flask app
app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
CORS(app)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'yolo_loaded': api.yolo_model is not None,
        'model_loaded': api.model is not None,
        'device': str(api.device),
        'classes': len(api.class_names) if api.class_names else 0
    })

# API endpoints (proxy to api.py)
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_proxy(path):
    """Proxy API requests to api.py"""
    from flask import request
    # Use the original WSGI environment to preserve file uploads and headers
    # verify path matches
    environ = request.environ.copy()
    # The path in environ is already correct (/api/...)
    
    with api.app.request_context(environ):
        try:
            response = api.app.full_dispatch_request()
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve React build or index.html"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))  # HF Spaces uses port 7860
    # Load models before starting
    print("⏳ Loading models...")
    api.load_models()
    
    print(f"🚀 PatiPedia starting on port {port}")
    print(f"🐱 YOLO loaded: {api.yolo_model is not None}")
    print(f"🧠 Model loaded: {api.model is not None}")
    print(f"💻 Device: {api.device}")
    
    if api.class_names:
        print(f"📊 Classes: {len(api.class_names)}")
    else:
        print("⚠️ Classes not loaded")
        
    app.run(host='0.0.0.0', port=port, debug=False)
