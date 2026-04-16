import random
from datetime import datetime

class RiskInferenceEngine:
    """
    Mock AI/ML Engine for assigning risk scores to incidents/locations.
    In a production scenario, this would load a Scikit-Learn or TensorFlow model
    trained on historical crime data, time-of-day risk matrices, and user movement anomalies.
    """
    
    def __init__(self):
        # self.model = load_model('risk_predictor_v1.pkl')
        pass

    def calculate_risk_score(self, latitude: float, longitude: float, time_of_day: datetime) -> float:
        """
        Calculates a risk score from 0.0 (Safe) to 100.0 (High Risk)
        """
        # Feature Extraction Mock
        hour = time_of_day.hour
        
        # Base factor based on time (night time = higher base risk)
        time_factor = 20.0
        if 20 <= hour or hour <= 4:
            time_factor = 60.0
            
        # Geographic variance (mocking dangerous zones vs safe zones)
        # Using a deterministic random based on coords just for demonstration
        geo_seed = int((latitude + longitude) * 1000)
        random.seed(geo_seed)
        geo_factor = random.uniform(0, 40)
        
        final_score = time_factor + geo_factor
        return min(max(final_score, 0.0), 100.0)

    def detect_fake_alert(self, user_history_len: int, seconds_active: int) -> bool:
        """
        Detects if an alert is likely an accidental pocket-dial.
        """
        if seconds_active < 3 and user_history_len > 10:
            # Typical pattern of pocket dials: triggered and immediately cancelled several times
            return True
        return False

# Singleton instance
risk_engine = RiskInferenceEngine()
