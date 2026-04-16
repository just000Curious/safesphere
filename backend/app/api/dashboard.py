from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.alert import Location
from typing import Dict, List, Any
from uuid import UUID

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    # Get today's date range
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Count active alerts
    active_alerts_result = await db.execute(
        select(func.count()).select_from(Alert).where(
            Alert.status.in_(["active", "acknowledged", "escalated"])
        )
    )
    active_alerts = active_alerts_result.scalar()
    
    # Count today's alerts
    today_alerts_result = await db.execute(
        select(func.count()).select_from(Alert).where(
            Alert.triggered_at >= today_start
        )
    )
    today_alerts = today_alerts_result.scalar()
    
    # Average response time (time from alert to acknowledgment)
    resolved_alerts_result = await db.execute(
        select(Alert).where(
            Alert.status == "resolved",
            Alert.acknowledged_at.isnot(None)
        )
    )
    resolved_alerts = resolved_alerts_result.scalars().all()
    
    response_times = []
    for alert in resolved_alerts:
        if alert.acknowledged_at:
            response_time = (alert.acknowledged_at - alert.triggered_at).total_seconds()
            response_times.append(response_time)
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Get alerts by severity
    severity_stats = {}
    for severity in ["low", "medium", "high", "critical"]:
        count_result = await db.execute(
            select(func.count()).select_from(Alert).where(Alert.severity == severity)
        )
        severity_stats[severity] = count_result.scalar()
    
    # Total users
    total_users_result = await db.execute(select(func.count()).select_from(User))
    total_users = total_users_result.scalar()
    
    # Recent incidents (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_incidents_result = await db.execute(
        select(func.count()).select_from(Incident).where(
            Incident.created_at >= seven_days_ago
        )
    )
    recent_incidents = recent_incidents_result.scalar()
    
    return {
        "active_alerts": active_alerts,
        "today_alerts": today_alerts,
        "avg_response_time_seconds": round(avg_response_time, 2),
        "severity_distribution": severity_stats,
        "total_users": total_users,
        "recent_incidents": recent_incidents
    }

@router.get("/alerts/timeline")
async def get_alerts_timeline(
    days: int = 7,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get alerts count for each day in the last N days"""
    dates = []
    counts = []
    
    for i in range(days):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        count_result = await db.execute(
            select(func.count()).select_from(Alert).where(
                and_(
                    Alert.triggered_at >= day_start,
                    Alert.triggered_at < day_end
                )
            )
        )
        count = count_result.scalar()
        
        dates.append(day_start.strftime("%Y-%m-%d"))
        counts.append(count)
    
    return {"dates": dates[::-1], "counts": counts[::-1]}

@router.get("/incidents/recent")
async def get_recent_incidents(
    limit: int = 20,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Incident)
        .order_by(Incident.created_at.desc())
        .limit(limit)
    )
    incidents = result.scalars().all()
    
    # Get user details for each incident
    incident_list = []
    for incident in incidents:
        # Get alert details
        alert_result = await db.execute(
            select(Alert).where(Alert.id == incident.alert_id)
        )
        alert = alert_result.scalar_one_or_none()
        
        # Get user details
        if alert:
            user_result = await db.execute(
                select(User).where(User.id == alert.user_id)
            )
            user = user_result.scalar_one_or_none()
            
            incident_list.append({
                "id": str(incident.id),
                "alert_id": str(incident.alert_id),
                "incident_type": incident.incident_type,
                "description": incident.description,
                "status": incident.status,
                "severity_score": incident.severity_score,
                "user_name": user.name if user else "Unknown",
                "user_phone": user.phone if user else "Unknown",
                "location": {
                    "lat": incident.location_lat,
                    "lng": incident.location_lng,
                    "address": incident.location_address
                },
                "created_at": incident.created_at.isoformat()
            })
    
    return incident_list

@router.get("/heatmap-data")
async def get_heatmap_data(
    days: int = 30,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    since_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(Alert).where(Alert.triggered_at >= since_date)
    )
    alerts = result.scalars().all()
    
    locations = []
    for alert in alerts:
        locations.append({
            "lat": alert.latitude,
            "lng": alert.longitude,
            "weight": 1,
            "severity": alert.severity,
            "timestamp": alert.triggered_at.isoformat()
        })
    
    return {"locations": locations}

@router.get("/users")
async def get_all_users_stats(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    users_result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = users_result.scalars().all()
    
    user_stats_list = []
    for user in users:
        alerts_result = await db.execute(select(func.count()).select_from(Alert).where(Alert.user_id == user.id))
        total_alerts = alerts_result.scalar()
        
        user_stats_list.append({
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "total_alerts": total_alerts
        })
        
    return user_stats_list
