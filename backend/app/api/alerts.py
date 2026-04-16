from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
import os
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from uuid import UUID
from app.schemas.alert import AlertTrigger, AlertResponse, AlertUpdate, LocationUpdate, LocationResponse
from app.models.alert import Alert, Location
from app.models.user import User, TrustedContact
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.services.notification import send_alert_notifications
from app.services.escalation import check_escalation_task
from app.core.websocket import manager

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.post("/trigger", response_model=AlertResponse)
async def trigger_alert(
    alert_data: AlertTrigger,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Create alert
    alert = Alert(
        user_id=current_user.id,
        status="active",
        severity=alert_data.severity,
        latitude=alert_data.latitude,
        longitude=alert_data.longitude,
        address=alert_data.address,
        triggered_at=datetime.utcnow(),
        escalation_count=0
    )
    
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    # Get user's trusted contacts
    result = await db.execute(
        select(TrustedContact).where(TrustedContact.user_id == current_user.id)
    )
    contacts = result.scalars().all()
    
    # Send notifications in background
    background_tasks.add_task(
        send_alert_notifications,
        current_user,
        alert,
        contacts
    )
    
    # Notify via WebSocket
    await manager.send_personal_message(
        {"type": "alert_triggered", "alert_id": str(alert.id)},
        str(current_user.id)
    )
    
    return AlertResponse.from_orm(alert)

@router.get("/active", response_model=List[AlertResponse])
async def get_active_alerts(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Alert).where(
            Alert.status.in_(["active", "acknowledged", "escalated"])
        ).order_by(Alert.triggered_at.desc())
    )
    alerts = result.scalars().all()
    
    return [AlertResponse.from_orm(alert) for alert in alerts]

@router.put("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check if user is authorized (alert owner or contact or admin)
    if current_user.role != "admin" and alert.user_id != current_user.id:
        # Check if user is a contact
        contact_result = await db.execute(
            select(TrustedContact).where(
                TrustedContact.user_id == alert.user_id,
                TrustedContact.phone == current_user.phone
            )
        )
        if not contact_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")
    
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Alert acknowledged"}

@router.put("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.id
    
    # Synthesize strict Incident Log structure locally
    from app.models.incident import Incident
    incident_log = Incident(
        alert_id=alert.id,
        incident_type="SOS Resolved",
        description=f"Admin {current_user.name} terminated alarm {alert.id}.",
        status="closed",
        severity_score=90 if alert.severity == "high" else 50,
        location_lat=alert.latitude,
        location_lng=alert.longitude,
        location_address=alert.address,
        created_at=datetime.utcnow(),
        resolved_at=datetime.utcnow()
    )
    db.add(incident_log)
    await db.commit()
    
    return {"message": "Alert physically resolved and logged safely into Incident Directory."}

@router.post("/locations/update")
async def update_location(
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Store location
    location = Location(
        user_id=current_user.id,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        address=location_data.address,
        accuracy=location_data.accuracy,
        speed=location_data.speed,
        heading=location_data.heading,
        timestamp=datetime.utcnow()
    )
    
    # Check if user has active alert
    result = await db.execute(
        select(Alert).where(
            Alert.user_id == current_user.id,
            Alert.status.in_(["active", "acknowledged", "escalated"])
        )
    )
    active_alert = result.scalar_one_or_none()
    
    if active_alert:
        location.alert_id = active_alert.id
    
    db.add(location)
    await db.commit()
    
    # Broadcast to contacts if there's an active alert
    if active_alert:
        # Get user's contacts
        contacts_result = await db.execute(
            select(TrustedContact).where(TrustedContact.user_id == current_user.id)
        )
        contacts = contacts_result.scalars().all()
        
        for contact in contacts:
            await manager.send_personal_message(
                {
                    "type": "location_update",
                    "user_id": str(current_user.id),
                    "location": location_data.dict(),
                    "alert_id": str(active_alert.id)
                },
                contact.phone  # Using phone as identifier for WebSocket
            )
    
    return {"message": "Location updated successfully"}

@router.get("/location-history/{user_id}", response_model=List[LocationResponse])
async def get_location_history(
    user_id: UUID,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Location)
        .where(Location.user_id == user_id)
        .order_by(Location.timestamp.desc())
        .limit(limit)
    )
    locations = result.scalars().all()
    return [LocationResponse.from_orm(loc) for loc in locations]

@router.post("/{alert_id}/audio")
async def upload_audio_evidence(
    alert_id: UUID,
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Secure the evidence chronologically
        evidence_dir = "uploads/evidence"
        os.makedirs(evidence_dir, exist_ok=True)
        file_path = f"{evidence_dir}/{alert_id}_{int(datetime.utcnow().timestamp())}.webm"
        
        content = await audio_file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
            
        return {"status": "Evidence Secured", "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
