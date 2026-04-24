# SafeSphere System Debugging Guide

## Current Status & Issues Found

### Issues Identified from Error Logs:

1. **Alembic Migration Issues** ✓ RESOLVED
   - Error: "Could not determine revision id from filename"
   - Cause: Earlier migration attempts failed
   - Solution: Migration files are correctly formatted now

2. **Configuration Issues** ⚠️ NEEDS VERIFICATION
   - DATABASE_URL was empty in .env
   - SMTP credentials incomplete
   - Status: **FIXED** - Updated .env with your credentials

3. **Service Connection Issues** ⏳ NEEDS TESTING
   - Database connection (PostgreSQL)
   - Email service (SMTP Gmail)
   - SMS service (Fast2SMS API)
   - WebSocket connection

---

## Pre-Flight Checklist

Before running the system, verify:

### 1. **Database Setup**
```bash
# Check PostgreSQL is running on Windows
# Open Services (services.msc) and verify PostgreSQL is running

# Or check from PowerShell
Get-Service PostgreSQL*

# Expected output: postgresql-x64-14 ... Running
```

**Your Database Credentials:**
- Host: localhost
- Port: 5432
- Database: safesphere
- User: postgres
- Password: postgres123

### 2. **Redis Setup**
```bash
# Check Redis is running
Get-Service Redis*

# Expected output: Redis ... Running
```

**Your Redis URL:** redis://localhost:6379

### 3. **Python Environment**
```bash
# Navigate to backend
cd g:\safesphere\backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 4. **Gmail App Password Setup** (IMPORTANT!)
Your SMTP settings:
- Host: smtp.gmail.com
- Port: 587
- User: sanketthorat786@gmail.com
- Password: bkeb ngak kaui fzbx

⚠️ **Note:** This appears to be a Gmail App Password (not your main password). Gmail requires:
1. 2-Factor Authentication enabled
2. App Password generated from account settings
3. Use that 16-character password in .env

---

## Testing Procedures

### Test 1: Run System Diagnostic
```bash
cd g:\safesphere\backend
python system_diagnostic.py
```

This will test:
- ✓ Configuration loading
- ✓ Database connection
- ✓ Email service
- ✓ SMS service
- ✓ WebSocket manager
- ✓ ML/Risk Engine
- ✓ API Router

### Test 2: Database Migrations
```bash
# Create all tables
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade...
# INFO  [alembic.runtime.migration] Running upgrade a97a2dc91791_initial_schema
# INFO  [alembic.runtime.migration] Running upgrade 5f72c9a24bd4_add_ai_fields
```

### Test 3: Run FastAPI Server
```bash
# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# Uvicorn running on http://0.0.0.0:8000
# Press CTRL+C to quit
```

### Test 4: Test API Endpoints
```bash
# In another terminal, test health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database":"connected"}
```

---

## Common Issues & Solutions

### Issue 1: PostgreSQL Connection Failed
```
Error: could not connect to server: Connection refused
```

**Solution:**
```powershell
# Check if PostgreSQL is running
Get-Service PostgreSQL*

# If not running, start it
Start-Service PostgreSQL14-x64

# Verify connection
psql -U postgres -h localhost -c "SELECT 1;"

# You'll be prompted for password: postgres123
```

### Issue 2: Database Does Not Exist
```
Error: database "safesphere" does not exist
```

**Solution:**
```powershell
# Connect to PostgreSQL
psql -U postgres -h localhost

# In psql prompt:
CREATE DATABASE safesphere;
\q

# Then run migrations
alembic upgrade head
```

### Issue 3: Gmail SMTP Authentication Failed
```
Error: (535, b'5.7.8 Username and password not accepted')
```

**Solution:**
1. Check your Gmail app password is correct (should be 16 characters)
2. Verify 2-Factor Authentication is enabled on your Gmail account
3. Generate a new app password:
   - Go to myaccount.google.com
   - Security > App passwords (or search "app passwords")
   - Select "Mail" and "Windows Computer"
   - Generate & copy the 16-character password
   - Update .env file

### Issue 4: Redis Connection Failed
```
Error: Error -1 connecting to localhost:6379. Name or service not known
```

**Solution:**
```powershell
# Check if Redis is running
Get-Service Redis*

# If not running, start it
Start-Service Redis

# Or install Redis if not present
choco install redis-64
```

### Issue 5: FastAPI Route Not Found
```
Error: 404 Not Found
```

**Solution:**
- Check router is included in main.py
- Verify API prefix (e.g., /alerts)
- Check endpoint exists in the router file

---

## Function-by-Function Testing

### Test Alert Triggering
```bash
# Register a user first
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "phone": "+919999999999",
    "password": "Test@123",
    "role": "user"
  }'

# Then create an alert
curl -X POST http://localhost:8000/alerts/trigger \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "latitude": 28.7041,
    "longitude": 77.1025,
    "address": "Delhi, India",
    "severity": "high"
  }'
```

### Test Email Notification
```python
import asyncio
from app.services.notification import send_email

async def test():
    await send_email(
        to_email="recipient@example.com",
        subject="SafeSphere Test",
        body="Testing email functionality"
    )

asyncio.run(test())
```

### Test SMS Notification
```python
import asyncio
from app.services.notification import send_sms

async def test():
    await send_sms(
        to_phone="+919999999999",
        message="SafeSphere SMS Test"
    )

asyncio.run(test())
```

### Test WebSocket Connection
```bash
# In browser console at http://localhost:8000
const ws = new WebSocket('ws://localhost:8000/ws/track/user-id');

ws.onopen = () => {
  console.log('Connected');
  ws.send(JSON.stringify({lat: 28.7041, lng: 77.1025}));
};

ws.onmessage = (event) => {
  console.log('Received:', event.data);
};
```

### Test Risk Scoring
```python
from datetime import datetime
from app.services.ml import risk_engine

# Calculate risk at a location
risk_score = risk_engine.calculate_risk_score(28.7041, 77.1025, datetime.now())
print(f"Risk score: {risk_score}")  # 0-100 scale

# Detect fake alert
is_fake = risk_engine.detect_fake_alert(user_history_len=5, seconds_active=1)
print(f"Is fake alert: {is_fake}")  # True if likely fake
```

---

## Startup Sequence (Step by Step)

1. **Start PostgreSQL**
   ```powershell
   Start-Service PostgreSQL14-x64
   ```

2. **Start Redis**
   ```powershell
   Start-Service Redis
   ```

3. **Activate Python Environment**
   ```powershell
   cd g:\safesphere\backend
   .\venv\Scripts\Activate.ps1
   ```

4. **Run Database Migrations**
   ```powershell
   alembic upgrade head
   ```

5. **Run System Diagnostic**
   ```powershell
   python system_diagnostic.py
   ```

6. **Start FastAPI Server**
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start Frontend (in another terminal)**
   ```powershell
   cd g:\safesphere\frontend
   npm install
   npm run dev
   ```

8. **Access the Application**
   - Frontend: http://localhost:5173
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## Monitoring & Logs

### Backend Logs
- Check console output for errors
- Look for: Database warnings, Service connection failures

### Frontend Logs
- Open browser DevTools (F12)
- Console tab shows JavaScript errors
- Network tab shows API calls

### Database Logs
```bash
# Check PostgreSQL logs
psql -U postgres -c "SELECT * FROM pg_log;"
```

---

## Next Steps

1. ✅ **Verify .env Configuration** - DONE
2. ⏳ **Run System Diagnostic** - NEXT
3. ⏳ **Run Database Migrations**
4. ⏳ **Start Server & Test Endpoints**
5. ⏳ **Test Each Function Individually**
6. ⏳ **End-to-End Integration Test**

---

## Support & Troubleshooting

If you encounter issues:

1. **Check the error message carefully** - Usually tells you exactly what's wrong
2. **Review the relevant section above** - Common issues have solutions
3. **Check service status** - Database, Redis running?
4. **Verify .env credentials** - Database password, SMTP settings
5. **Review logs** - Both FastAPI console and browser console
6. **Test component in isolation** - Use system_diagnostic.py

---

Generated: 2026-04-24
Status: Configuration Complete, Ready for Testing
