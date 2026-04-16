from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import traceback
from fastapi import Request, responses
from app.core.database import engine, Base
from app.api import auth, users, alerts, dashboard
from app.services.escalation import check_escalation_task

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start background tasks
    asyncio.create_task(check_escalation_task())
    
    yield
    
    # Shutdown
    await engine.dispose()

app = FastAPI(title="SafeSphere API", version="1.0.0", lifespan=lifespan)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return responses.JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "traceback": traceback.format_exc()
        }
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import auth, users, alerts, dashboard, websockets

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
app.include_router(websockets.router)

@app.get("/")
async def root():
    return {"message": "SafeSphere API", "version": "1.0.0", "database": "PostgreSQL"}

@app.get("/health")
async def health_check():
    try:
        # Check database connection
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
