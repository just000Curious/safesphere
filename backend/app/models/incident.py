from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id", ondelete="CASCADE"), unique=True, nullable=False)
    incident_type = Column(String(100), nullable=False)  # harassment, assault, medical, etc.
    description = Column(Text, nullable=True)
    status = Column(String(50), default="open")  # open, investigating, closed
    severity_score = Column(Integer, default=1)  # 1-5
    police_notified = Column(Boolean, default=False)
    medical_required = Column(Boolean, default=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    location_address = Column(Text)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alert = relationship("Alert", back_populates="incident")
    evidence = relationship("Evidence", back_populates="incident", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String(50), nullable=False)  # audio, video, photo, text
    file_url = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    file_metadata = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    incident = relationship("Incident", back_populates="evidence")
    uploader = relationship("User")
