"""
SafeSphere Comprehensive API Test Suite
Tests all endpoints and functions
"""
import asyncio
import json
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test_user@safesphere.com",
    "name": "Test User",
    "phone": "+919876543210",
    "password": "TestPassword@123",
    "role": "user"
}
TEST_CONTACT = {
    "email": "contact@safesphere.com",
    "name": "Emergency Contact",
    "phone": "+919999999999",
    "password": "ContactPassword@123",
    "role": "contact"
}

class TestSuite:
    def __init__(self):
        self.access_token = None
        self.user_id = None
        self.alert_id = None
        self.contact_id = None
        
    async def test_health_check(self):
        """Test 1: Health Check"""
        print("\n[1] Testing Health Check...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                print("✓ Health check passed")
                print(f"  Status: {data['status']}")
                print(f"  Database: {data['database']}")
                return True
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            return False

    async def test_register_user(self):
        """Test 2: User Registration"""
        print("\n[2] Testing User Registration...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/auth/register",
                    json=TEST_USER
                )
                assert response.status_code == 200
                data = response.json()
                self.user_id = data["id"]
                assert data["email"] == TEST_USER["email"]
                print("✓ User registration passed")
                print(f"  User ID: {self.user_id}")
                print(f"  Email: {data['email']}")
                return True
        except Exception as e:
            print(f"✗ User registration failed: {e}")
            return False

    async def test_login(self):
        """Test 3: User Login"""
        print("\n[3] Testing User Login...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/auth/login",
                    json={
                        "email": TEST_USER["email"],
                        "password": TEST_USER["password"]
                    }
                )
                assert response.status_code == 200
                data = response.json()
                self.access_token = data["access_token"]
                assert data["token_type"] == "bearer"
                print("✓ User login passed")
                print(f"  Token: {self.access_token[:30]}...")
                return True
        except Exception as e:
            print(f"✗ User login failed: {e}")
            return False

    async def test_add_trusted_contact(self):
        """Test 4: Add Trusted Contact"""
        print("\n[4] Testing Add Trusted Contact...")
        try:
            # First register the contact
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/auth/register",
                    json=TEST_CONTACT
                )
                assert response.status_code == 200
                contact_data = response.json()
                self.contact_id = contact_data["id"]
                
                # Then add as trusted contact
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = await client.post(
                    f"{BASE_URL}/users/contacts",
                    headers=headers,
                    json={
                        "contact_id": self.contact_id,
                        "relationship": "friend",
                        "is_primary": True
                    }
                )
                assert response.status_code == 200
                print("✓ Add trusted contact passed")
                print(f"  Contact ID: {self.contact_id}")
                print(f"  Relationship: friend")
                return True
        except Exception as e:
            print(f"✗ Add trusted contact failed: {e}")
            return False

    async def test_trigger_alert(self):
        """Test 5: Trigger Emergency Alert"""
        print("\n[5] Testing Trigger Emergency Alert...")
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = await client.post(
                    f"{BASE_URL}/alerts/trigger",
                    headers=headers,
                    json={
                        "latitude": 28.7041,
                        "longitude": 77.1025,
                        "address": "Delhi, India",
                        "severity": "high"
                    }
                )
                assert response.status_code == 200
                data = response.json()
                self.alert_id = data["id"]
                assert data["status"] == "active"
                assert data["severity"] == "high"
                print("✓ Trigger alert passed")
                print(f"  Alert ID: {self.alert_id}")
                print(f"  Status: {data['status']}")
                print(f"  Severity: {data['severity']}")
                print(f"  Location: {data['address']}")
                return True
        except Exception as e:
            print(f"✗ Trigger alert failed: {e}")
            return False

    async def test_get_active_alerts(self):
        """Test 6: Get Active Alerts (Admin)"""
        print("\n[6] Testing Get Active Alerts...")
        try:
            # Register and login as admin
            admin_data = {
                "email": "admin@safesphere.com",
                "name": "Admin User",
                "phone": "+918888888888",
                "password": "AdminPassword@123",
                "role": "admin"
            }
            async with httpx.AsyncClient() as client:
                # Register admin
                response = await client.post(
                    f"{BASE_URL}/auth/register",
                    json=admin_data
                )
                
                # Login as admin
                response = await client.post(
                    f"{BASE_URL}/auth/login",
                    json={
                        "email": admin_data["email"],
                        "password": admin_data["password"]
                    }
                )
                admin_token = response.json()["access_token"]
                
                # Get active alerts
                headers = {"Authorization": f"Bearer {admin_token}"}
                response = await client.get(
                    f"{BASE_URL}/alerts/active",
                    headers=headers
                )
                assert response.status_code == 200
                data = response.json()
                print("✓ Get active alerts passed")
                print(f"  Active alerts count: {len(data)}")
                return True
        except Exception as e:
            print(f"✗ Get active alerts failed: {e}")
            return False

    async def test_acknowledge_alert(self):
        """Test 7: Acknowledge Alert"""
        print("\n[7] Testing Acknowledge Alert...")
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = await client.put(
                    f"{BASE_URL}/alerts/{self.alert_id}/acknowledge",
                    headers=headers
                )
                assert response.status_code == 200
                print("✓ Acknowledge alert passed")
                print(f"  Alert ID: {self.alert_id}")
                print(f"  Status updated")
                return True
        except Exception as e:
            print(f"✗ Acknowledge alert failed: {e}")
            return False

    async def test_location_update(self):
        """Test 8: Location Update"""
        print("\n[8] Testing Location Update...")
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = await client.post(
                    f"{BASE_URL}/locations/update",
                    headers=headers,
                    json={
                        "alert_id": str(self.alert_id),
                        "latitude": 28.7050,
                        "longitude": 77.1035,
                        "accuracy": 10.5,
                        "speed": 0.0,
                        "heading": 0.0
                    }
                )
                # Note: Might be 200 or 201 depending on implementation
                assert response.status_code in [200, 201]
                print("✓ Location update passed")
                print(f"  New coordinates: 28.7050, 77.1035")
                return True
        except Exception as e:
            print(f"✗ Location update failed: {e}")
            return False

    async def test_resolve_alert(self):
        """Test 9: Resolve Alert"""
        print("\n[9] Testing Resolve Alert...")
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = await client.put(
                    f"{BASE_URL}/alerts/{self.alert_id}/resolve",
                    headers=headers
                )
                assert response.status_code == 200
                print("✓ Resolve alert passed")
                print(f"  Alert ID: {self.alert_id}")
                print(f"  Status: resolved")
                return True
        except Exception as e:
            print(f"✗ Resolve alert failed: {e}")
            return False

    async def test_get_user_profile(self):
        """Test 10: Get User Profile"""
        print("\n[10] Testing Get User Profile...")
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = await client.get(
                    f"{BASE_URL}/users/me",
                    headers=headers
                )
                assert response.status_code == 200
                data = response.json()
                assert data["email"] == TEST_USER["email"]
                print("✓ Get user profile passed")
                print(f"  Email: {data['email']}")
                print(f"  Name: {data['name']}")
                print(f"  Phone: {data['phone']}")
                return True
        except Exception as e:
            print(f"✗ Get user profile failed: {e}")
            return False

    async def run_all_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("SafeSphere API Comprehensive Test Suite")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_register_user,
            self.test_login,
            self.test_add_trusted_contact,
            self.test_trigger_alert,
            self.test_get_active_alerts,
            self.test_acknowledge_alert,
            self.test_location_update,
            self.test_resolve_alert,
            self.test_get_user_profile,
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                print(f"Unexpected error: {e}")
                results.append(False)
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        passed = sum(results)
        total = len(results)
        print(f"\nPassed: {passed}/{total} tests")
        
        if passed == total:
            print("\n✓ All tests passed! System is operational.")
            return 0
        else:
            print(f"\n✗ {total - passed} test(s) failed. Review logs above.")
            return 1

async def main():
    suite = TestSuite()
    exit_code = await suite.run_all_tests()
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        exit(1)
