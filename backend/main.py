import os
import logging
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from .database import engine, Base
from .models import User, PatientProfile, Hospital  # Import models to register them with Base metadata
from .routers import auth, hospital, profile

# Configure application logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

# Initialize FastAPI application
app = FastAPI(
    title="Healthcare Delivery API",
    description="Backend API for Svasthya Healthcare Delivery Application powered by FastAPI and SQLAlchemy.",
    version="1.0.0"
)

# --- CORS Configuration ---
# For development, allow local Flutter web/emulator origins. Restrict strictly in production.
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://10.0.2.2:8000",  # Android Emulator default loopback
    "*"  # Note: Tighten this to explicit domains before production deployment
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# --- Database Table Initialization ---
# Development convenience: creates tables if they don't exist.
# Production Note: Use Alembic migrations (`alembic revision --autogenerate`) instead of `create_all()`.
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully via SQLAlchemy metadata.")
except Exception as e:
    logger.error(f"Error initializing database tables: {e}")

# --- Register Routers ---
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(hospital.router, prefix="/hospitals", tags=["Hospitals"])
app.include_router(profile.router, prefix="/profiles", tags=["Patient Profiles"])


# --- Root & Health Check Endpoints ---
@app.get("/", tags=["Root"])
def root():
    return {
        "status": "online",
        "message": "Welcome to Svasthya Healthcare Delivery API",
        "docs_url": "/docs"
    }


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint to verify API and database connectivity."""
    db_status = "connected"
    try:
        # Simple query test to verify DB responsiveness
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        db_status = "disconnected"

    status_code = status.HTTP_200_OK if db_status == "connected" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "api_status": "healthy",
        "database_status": db_status,
        "service_message": "Svasthya backend service is operational."
    }
    
