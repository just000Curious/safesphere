from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, JSON, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import sqlalchemy.orm as orm
from datetime import datetime
import uuid
from app.core.database import Base

# Association table for user-contacts relationship
user_contacts = Table(
    'user_contacts',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE')),
    Column('contact_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE')),
    Column('relationship', String(100)),
    Column('is_primary', Boolean, default=False),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # user, contact, admin
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan", foreign_keys="[Alert.user_id]")
    locations = relationship("Location", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    # Many-to-many relationship for emergency contacts
    emergency_contacts = relationship(
        "User",
        secondary=user_contacts,
        primaryjoin=id == user_contacts.c.user_id,
        secondaryjoin=id == user_contacts.c.contact_id,
        backref="contact_of"
    )

class TrustedContact(Base):
    __tablename__ = "trusted_contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255))
    relationship = Column(String(100), nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = orm.relationship("User", backref="custom_contacts")
