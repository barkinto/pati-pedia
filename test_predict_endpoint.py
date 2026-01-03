
import requests
import io

def test_predict():
    # Download a sample cat image
    img_url = "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"
    print(f"Downloading sample image from {img_url}...")
    try:
        img_response = requests.get(img_url, timeout=10)
        img_response.raise_for_status()
    except Exception as e:
        print(f"Failed to download image: {e}")
        return

    # Test predict endpoint
    url = "http://localhost:7860/api/predict"
    files = {'image': ('cat.jpg', img_response.content, 'image/jpeg')}
    
    print(f"Sending POST request to {url}...")
    try:
        response = requests.post(url, files=files, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response JSON:")
            print(response.json())
        else:
            print("Error Response:")
            print(response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_predict()
