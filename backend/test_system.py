import urllib.request
import urllib.error
import urllib.parse
import json

def report(name, status, details=""):
    print(f"[{'PASS' if status else 'FAIL'}] {name} {('- ' + details) if details else ''}")

print("--- System Diagnostic Check ---")

# 1. Check Dashboard Stats GET
try:
    resp = urllib.request.urlopen('http://localhost:8000/dashboard/stats')
    data = json.loads(resp.read().decode())
    report("Admin Dashboard Stats endpoint", True)
except urllib.error.HTTPError as e:
    report("Admin Dashboard Stats endpoint", False, f"HTTP {e.code}: {e.read().decode()}")

# 2. Check Alerts Timeline GET
try:
    resp = urllib.request.urlopen('http://localhost:8000/dashboard/alerts/timeline')
    report("Admin Dashboard Timeline endpoint", True)
except urllib.error.HTTPError as e:
    report("Admin Dashboard Timeline endpoint", False, f"HTTP {e.code}: {e.read().decode()}")

# 3. Check Contacts GET
try:
    resp = urllib.request.urlopen('http://localhost:8000/users/contacts')
    report("Contacts GET endpoint", True)
except urllib.error.HTTPError as e:
    report("Contacts GET endpoint", False, f"HTTP {e.code}: {e.read().decode()}")

# 4. Check SOS Trigger POST
try:
    payload = json.dumps({"severity": "high", "latitude": 28.1, "longitude": 77.1, "address": "Test"}).encode('utf-8')
    req = urllib.request.Request('http://localhost:8000/alerts/trigger', data=payload, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    report("SOS Trigger POST endpoint", True)
except urllib.error.HTTPError as e:
    report("SOS Trigger POST endpoint", False, f"HTTP {e.code}: {e.read().decode()}")
except Exception as e:
    report("SOS Trigger POST endpoint", False, str(e))

# 5. Check Add Contact POST
try:
    payload = json.dumps({"name": "Test Contact", "phone": "+19999999999", "email": "test@test.com", "relationship": "family", "is_primary": True}).encode('utf-8')
    req = urllib.request.Request('http://localhost:8000/users/contacts', data=payload, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    report("Contacts POST endpoint", True)
except urllib.error.HTTPError as e:
    report("Contacts POST endpoint", False, f"HTTP {e.code}: {e.read().decode()}")
except Exception as e:
    report("Contacts POST endpoint", False, str(e))
