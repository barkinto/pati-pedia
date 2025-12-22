#!/usr/bin/env python3
"""
Script to update Gemini API key in project files
"""

import os
import sys
import re

def update_api_key_in_file(file_path, new_key, pattern, replacement_template):
    """Update API key in a file"""
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if key is already updated
        if new_key in content:
            print(f"✅ Key already in {file_path}")
            return True
        
        # Replace old key with new key
        updated_content = re.sub(pattern, replacement_template.format(new_key), content)
        
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ Updated {file_path}")
            return True
        else:
            print(f"⚠️  No changes needed in {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("🔑 Gemini API Key Güncelleme Scripti")
        print("=" * 50)
        print("")
        print("Kullanım:")
        print(f"  python3 {sys.argv[0]} YOUR_NEW_API_KEY")
        print("")
        print("Örnek:")
        print(f"  python3 {sys.argv[0]} AIzaSy...")
        print("")
        sys.exit(1)
    
    new_key = sys.argv[1].strip()
    
    if not new_key.startswith('AIzaSy'):
        print("⚠️  API key 'AIzaSy' ile başlamalı!")
        response = input("Devam etmek istiyor musunuz? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print(f"🔑 Yeni API key: {new_key[:20]}...")
    print("")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Pattern to match old API keys
    old_key_pattern = r"AIzaSy[A-Za-z0-9_-]+"
    
    # Files to update
    files_to_update = [
        {
            'path': os.path.join(project_dir, 'api.py'),
            'pattern': r"api_key = os\.getenv\('GEMINI_API_KEY', '{}'\)".format(old_key_pattern),
            'replacement': "api_key = os.getenv('GEMINI_API_KEY', '{}')"
        },
        {
            'path': os.path.join(project_dir, 'start_api.sh'),
            'pattern': r"export GEMINI_API_KEY=\"{}\"".format(old_key_pattern),
            'replacement': 'export GEMINI_API_KEY="{}"'
        }
    ]
    
    success_count = 0
    for file_info in files_to_update:
        if update_api_key_in_file(
            file_info['path'],
            new_key,
            file_info['pattern'],
            file_info['replacement']
        ):
            success_count += 1
    
    print("")
    print("=" * 50)
    if success_count > 0:
        print(f"✅ {success_count} dosya güncellendi!")
        print("")
        print("📋 Sonraki adımlar:")
        print("1. Projeyi yeniden başlatın:")
        print("   pkill -f 'desktop_app|api.py'")
        print("   python3 desktop_app.py")
        print("")
        print("2. Yeni key'i test edin:")
        print(f"   ./test_gemini_key.sh {new_key}")
    else:
        print("⚠️  Hiçbir dosya güncellenmedi. Manuel olarak kontrol edin.")
    
    print("")

if __name__ == '__main__':
    main()

