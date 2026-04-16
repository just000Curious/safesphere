import requests
import streamlit as st
from typing import Optional, Dict, Any, List
from uuid import UUID

class SafeSphereAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.role = None
    
    def set_token(self, token: str, user_id: str, role: str):
        self.token = token
        self.user_id = user_id
        self.role = role
        st.session_state['token'] = token
        st.session_state['user_id'] = user_id
        st.session_state['role'] = role
    
    def clear_token(self):
        self.token = None
        self.user_id = None
        self.role = None
        for key in ['token', 'user_id', 'role']:
            if key in st.session_state:
                del st.session_state[key]
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def register(self, email: str, name: str, phone: str, password: str, role: str = "user") -> Dict:
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json={
                    "email": email,
                    "name": name,
                    "phone": phone,
                    "password": password,
                    "role": role
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if hasattr(e, 'response') and e.response is not None:
                st.error(f"Backend Error: {e.response.text}")
            else:
                st.error(f"Connection Error: {str(e)}")
            return {"error": str(e)}
    
    def login(self, email: str, password: str) -> Optional[Dict]:
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.set_token(data['access_token'], data['user_id'], data['role'])
                return data
            else:
                st.error(f"Login failed: {response.text}")
                return None
        except Exception as e:
            st.error(f"Network error: {str(e)}")
            return None
    
    def get_user_info(self) -> Dict:
        response = requests.get(
            f"{self.base_url}/users/me",
            headers=self._get_headers()
        )
        return response.json()
    
    def add_contact(self, name: str, phone: str, relationship: str, email: Optional[str] = None, is_primary: bool = False) -> Dict:
        response = requests.post(
            f"{self.base_url}/users/contacts",
            headers=self._get_headers(),
            json={
                "name": name,
                "phone": phone,
                "email": email,
                "relationship": relationship,
                "is_primary": is_primary
            }
        )
        return response.json()
    
    def get_contacts(self) -> List[Dict]:
        response = requests.get(
            f"{self.base_url}/users/contacts",
            headers=self._get_headers()
        )
        return response.json()
    
    def trigger_alert(self, latitude: float, longitude: float, address: Optional[str] = None, severity: str = "high") -> Dict:
        response = requests.post(
            f"{self.base_url}/alerts/trigger",
            headers=self._get_headers(),
            json={
                "latitude": latitude,
                "longitude": longitude,
                "address": address,
                "severity": severity
            }
        )
        return response.json()
    
    def update_location(self, latitude: float, longitude: float, address: Optional[str] = None) -> Dict:
        response = requests.post(
            f"{self.base_url}/alerts/locations/update",
            headers=self._get_headers(),
            json={
                "latitude": latitude,
                "longitude": longitude,
                "address": address
            }
        )
        return response.json()
    
    def get_active_alerts(self) -> List[Dict]:
        response = requests.get(
            f"{self.base_url}/alerts/active",
            headers=self._get_headers()
        )
        return response.json()
    
    def acknowledge_alert(self, alert_id: str) -> Dict:
        response = requests.put(
            f"{self.base_url}/alerts/{alert_id}/acknowledge",
            headers=self._get_headers()
        )
        return response.json()
    
    def resolve_alert(self, alert_id: str) -> Dict:
        response = requests.put(
            f"{self.base_url}/alerts/{alert_id}/resolve",
            headers=self._get_headers()
        )
        return response.json()
    
    def get_dashboard_stats(self) -> Dict:
        response = requests.get(
            f"{self.base_url}/dashboard/stats",
            headers=self._get_headers()
        )
        return response.json()
    
    def get_recent_incidents(self) -> List[Dict]:
        response = requests.get(
            f"{self.base_url}/dashboard/incidents/recent",
            headers=self._get_headers()
        )
        return response.json()
    
    def get_heatmap_data(self, days: int = 30) -> Dict:
        response = requests.get(
            f"{self.base_url}/dashboard/heatmap-data",
            headers=self._get_headers(),
            params={"days": days}
        )
        return response.json()
