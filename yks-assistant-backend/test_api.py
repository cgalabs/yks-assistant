import requests
import time
import io
from PIL import Image

BASE_URL = "http://localhost:8000"

def wait_for_server():
    print("Waiting for server...")
    for _ in range(10):
        try:
            resp = requests.get(f"{BASE_URL}/health")
            if resp.status_code == 200:
                print("Server is up!")
                return True
        except:
            pass
        time.sleep(2)
    print("Server failed to start.")
    return False

def test_generate():
    print("\n[TEST] /generate")
    payload = {"topic": "Mutlak Değer", "difficulty": "medium"}
    resp = requests.post(f"{BASE_URL}/generate", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")

def test_coach():
    print("\n[TEST] /coach")
    payload = {"context": {"last_score": 80, "weakness": "Trigonometri"}}
    resp = requests.post(f"{BASE_URL}/coach", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")

def test_solve():
    print("\n[TEST] /solve")
    # Create dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    files = {'file': ('test.png', img_byte_arr, 'image/png')}
    resp = requests.post(f"{BASE_URL}/solve", files=files)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")

if __name__ == "__main__":
    if wait_for_server():
        test_generate()
        test_coach()
        test_solve()
