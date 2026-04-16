import urllib.request
import urllib.error
import json

def fetch_safe(url):
    try:
        urllib.request.urlopen(url)
        print(f"SUCCESS: {url}")
    except urllib.error.HTTPError as e:
        print(f"HTTP ERROR {e.code} on {url}:")
        print(e.read().decode())
    except Exception as e:
        print(f"Generic error on {url}: {str(e)}")

print("Testing endpoints...")
fetch_safe('http://localhost:8000/dashboard/stats')
fetch_safe('http://localhost:8000/users/contacts')
