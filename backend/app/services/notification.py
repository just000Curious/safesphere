import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from app.config import settings
from app.models.user import User
from app.models.alert import Alert
from app.models.notification import Notification
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
import asyncio

async def send_email(to_email: str, subject: str, body: str):
    """Send email notification"""
    if not settings.smtp_user or not settings.smtp_password:
        print(f"Email would be sent to {to_email}: {subject}")
        return True
    
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        
        msg.attach(MIMEText(body, "plain"))
        
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
        server.quit()
        
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

async def send_sms(to_phone: str, message: str):
    """Send SMS notification using Twilio"""
    if not settings.twilio_account_sid:
        print(f"SMS would be sent to {to_phone}: {message[:160]}")
        return True
    
    try:
        from twilio.rest import Client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
        message = client.messages.create(
            body=message[:160],  # SMS character limit
            from_=settings.twilio_phone_number,
            to=to_phone
        )
        
        print(f"SMS sent to {to_phone}, SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False

async def send_alert_notifications(
    user: User,
    alert: Alert,
    contacts: List,
    db: AsyncSession = None
):
    """Send notifications to all emergency contacts"""
    message = f"""
EMERGENCY ALERT from {user.name}!

Location: {alert.address or f"Lat: {alert.latitude}, Lng: {alert.longitude}"}
Time: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
Severity: {alert.severity.upper()}

Please check on them immediately. If you're a trusted contact, please acknowledge this alert.
"""
    
    for contact in contacts:
        # Send SMS
        sms_sent = False
        if contact.phone:
            sms_sent = await send_sms(contact.phone, message[:160])
        
        # Send Email
        email_sent = False
        if contact.email:
            email_sent = await send_email(
                contact.email,
                f"Emergency Alert: {user.name} needs help",
                message
            )
        
        # Store notification in database
        if db:
            notification = Notification(
                user_id=user.id,
                alert_id=alert.id,
                notification_type="sms" if sms_sent else "email",
                recipient=contact.phone or contact.email,
                message=message,
                status="sent" if (sms_sent or email_sent) else "failed",
                sent_at=datetime.utcnow()
            )
            db.add(notification)
    
    if db:
        await db.commit()
