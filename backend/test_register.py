import requests
import json

def test_register():
    url = "http://localhost:8000/auth/register"
    data = {
        "email": "test_register@example.com",
        "name": "Test User",
        "phone": "9998887776",
        "password": "testpassword",
        "role": "user"
    }
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_register()
