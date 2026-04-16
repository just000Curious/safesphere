from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class AlertTrigger(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    severity: Optional[str] = "high"

class AlertResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    severity: str
    latitude: float
    longitude: float
    address: Optional[str]
    triggered_at: datetime
    acknowledged_at: Optional[datetime]
    escalated_at: Optional[datetime]
    resolved_at: Optional[datetime]
    audio_recording_url: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[UUID] = None

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None

class LocationResponse(BaseModel):
    id: UUID
    user_id: UUID
    alert_id: Optional[UUID]
    latitude: float
    longitude: float
    address: Optional[str]
    accuracy: Optional[float]
    speed: Optional[float]
    heading: Optional[float]
    timestamp: datetime
    
    class Config:
        from_attributes = True
