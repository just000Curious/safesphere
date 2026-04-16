from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.alert import Alert
from app.models.user import User
from app.config import settings
import asyncio

async def check_escalation_task():
    """Background task to check for alerts needing escalation"""
    while True:
        await check_escalation()
        await check_unresolved_escalation()
        await asyncio.sleep(60)  # Check every minute

async def check_escalation():
    """Check for active alerts that haven't been acknowledged"""
    async with AsyncSessionLocal() as db:
        timeout_time = datetime.utcnow() - timedelta(seconds=settings.escalation_timeout_seconds)
        
        # Find alerts that are active and not acknowledged
        result = await db.execute(
            select(Alert).where(
                Alert.status == "active",
                Alert.triggered_at < timeout_time
            )
        )
        alerts_to_escalate = result.scalars().all()
        
        for alert in alerts_to_escalate:
            # Update alert status
            alert.status = "escalated"
            alert.escalated_at = datetime.utcnow()
            alert.escalation_count += 1
            await db.commit()
            
            # Notify admin dashboard (WebSocket)
            from app.core.websocket import manager
            await manager.broadcast_to_admins({
                "type": "alert_escalated",
                "alert_id": str(alert.id),
                "user_id": str(alert.user_id)
            })

async def check_unresolved_escalation():
    """Check for escalated alerts that remain unresolved"""
    async with AsyncSessionLocal() as db:
        unresolved_time = datetime.utcnow() - timedelta(minutes=settings.unresolved_escalation_minutes)
        
        result = await db.execute(
            select(Alert).where(
                Alert.status == "escalated",
                Alert.escalated_at < unresolved_time
            )
        )
        unresolved_alerts = result.scalars().all()
        
        for alert in unresolved_alerts:
            # Critical escalation - notify all admins
            admin_result = await db.execute(
                select(User).where(User.role == "admin")
            )
            admins = admin_result.scalars().all()
            
            from app.services.notification import send_sms
            
            for admin in admins:
                if admin.phone:
                    await send_sms(
                        admin.phone,
                        f"CRITICAL: Unresolved alert {alert.id} for user {alert.user_id}"
                    )
