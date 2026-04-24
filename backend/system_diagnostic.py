"""
SafeSphere System Diagnostic & Testing Script
Tests all major components and functions
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Import required modules
print("=" * 80)
print("SafeSphere System Diagnostic Test")
print("=" * 80)

# 1. Test Configuration Loading
print("\n[1/7] Testing Configuration Loading...")
try:
    from app.config import settings
    print("✓ Config loaded successfully")
    print(f"  - Database: {settings.database_url[:50]}...")
    print(f"  - Redis: {settings.redis_url}")
    print(f"  - SMTP: {settings.smtp_host}:{settings.smtp_port}")
    print(f"  - Email User: {settings.smtp_user}")
except Exception as e:
    print(f"✗ Config loading failed: {e}")
    sys.exit(1)

# 2. Test Database Connection
print("\n[2/7] Testing Database Connection...")
async def test_database():
    try:
        from sqlalchemy import text
        from app.core.database import engine
        
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
            print(f"  - URL: {settings.database_url}")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        return False

db_status = asyncio.run(test_database())

# 3. Test Email Service
print("\n[3/7] Testing Email Service...")
async def test_email():
    try:
        from app.services.notification import send_email
        
        # Test email sending (in test mode)
        result = await send_email(
            to_email=settings.smtp_user,
            subject="SafeSphere Email Test",
            body="This is a test email from SafeSphere system diagnostic."
        )
        print("✓ Email service connection successful")
        print(f"  - SMTP Host: {settings.smtp_host}")
        print(f"  - SMTP Port: {settings.smtp_port}")
        print(f"  - From: {settings.smtp_user}")
        return True
    except Exception as e:
        print(f"✗ Email service failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        return False

email_status = asyncio.run(test_email())

# 4. Test SMS Service
print("\n[4/7] Testing SMS Service...")
async def test_sms():
    try:
        from app.services.notification import send_sms
        
        # Test SMS sending (in test mode)
        result = await send_sms(
            to_phone="+919999999999",
            message="SafeSphere SMS Test - System Diagnostic"
        )
        print("✓ SMS service connection successful")
        print(f"  - Fast2SMS API Key configured: {bool(settings.fast2sms_api_key)}")
        return True
    except Exception as e:
        print(f"✗ SMS service failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        return False

sms_status = asyncio.run(test_sms())

# 5. Test WebSocket Connection
print("\n[5/7] Testing WebSocket Manager...")
try:
    from app.core.websocket import manager
    print("✓ WebSocket manager initialized")
    print(f"  - Host: {settings.websocket_host}")
    print(f"  - Port: {settings.websocket_port}")
    websocket_status = True
except Exception as e:
    print(f"✗ WebSocket manager failed: {e}")
    websocket_status = False

# 6. Test Risk Engine (ML)
print("\n[6/7] Testing Risk Inference Engine...")
try:
    from app.services.ml import risk_engine
    from datetime import datetime
    
    # Test risk scoring
    risk_score = risk_engine.calculate_risk_score(28.7041, 77.1025, datetime.now())
    print("✓ Risk inference engine operational")
    print(f"  - Sample risk score (Delhi): {risk_score:.2f}")
    
    # Test fake alert detection
    is_fake = risk_engine.detect_fake_alert(user_history_len=15, seconds_active=2)
    print(f"  - Fake alert detection: {is_fake}")
    ml_status = True
except Exception as e:
    print(f"✗ Risk engine failed: {e}")
    ml_status = False

# 7. Test API Router
print("\n[7/7] Testing API Router...")
try:
    from app.main import app
    print("✓ FastAPI app initialized successfully")
    print(f"  - Title: {app.title}")
    print(f"  - Version: {app.version}")
    
    # Check router count
    router_count = len(app.routes)
    print(f"  - Total routes configured: {router_count}")
    api_status = True
except Exception as e:
    print(f"✗ API router failed: {e}")
    api_status = False

# Summary Report
print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)

status_summary = {
    "✓ Configuration": True,
    "✓ Database": db_status,
    "✓ Email Service": email_status,
    "✓ SMS Service": sms_status,
    "✓ WebSocket": websocket_status,
    "✓ ML/Risk Engine": ml_status,
    "✓ API Router": api_status,
}

passed = sum(1 for v in status_summary.values() if v)
total = len(status_summary)

print("\nComponent Status:")
for component, status in status_summary.items():
    symbol = "✓" if status else "✗"
    print(f"  [{symbol}] {component}")

print(f"\nResult: {passed}/{total} components operational")

if passed == total:
    print("\n🎉 All systems operational! Ready for production deployment.")
    sys.exit(0)
else:
    print(f"\n⚠️  {total - passed} component(s) need attention.")
    print("\nCommon Issues & Fixes:")
    print("  1. Database: Ensure PostgreSQL is running and DATABASE_URL is correct")
    print("  2. Email: Check SMTP credentials (Gmail requires app-specific passwords)")
    print("  3. SMS: Verify Fast2SMS API key in .env file")
    print("  4. WebSocket: Check if port 8001 is available")
    print("  5. ML: Ensure datetime module is imported correctly")
    sys.exit(1)
