from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class IncidentCreate(BaseModel):
    alert_id: UUID
    incident_type: str
    description: Optional[str] = None
    severity_score: int = 1
    police_notified: bool = False
    medical_required: bool = False

class IncidentResponse(BaseModel):
    id: UUID
    alert_id: UUID
    incident_type: str
    description: Optional[str]
    status: str
    severity_score: int
    police_notified: bool
    medical_required: bool
    location_lat: float
    location_lng: float
    location_address: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class EvidenceCreate(BaseModel):
    evidence_type: str
    file_url: Optional[str] = None
    content: Optional[str] = None
    file_metadata: Optional[dict] = None

class EvidenceResponse(BaseModel):
    id: UUID
    incident_id: UUID
    evidence_type: str
    file_url: Optional[str]
    content: Optional[str]
    file_metadata: Optional[dict]
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
