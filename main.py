# main.py - FIXED VERSION with better error handling
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import uvicorn
import os
from datetime import datetime
from pathlib import Path
from config.settings import CORS_ORIGINS
from routers import auth, predict, history, admin
from utils.model_loader import get_model
from config.database import AsyncSessionLocal, async_engine, Base
from models.database import Database

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager (FastAPI 2.0+)"""
    # Startup
    print("🚀 Starting up Plant Disease API...")
    
    # 0. Create necessary directories
    os.makedirs("data/images", exist_ok=True)
    print("✅ Image directory verified")
    
    # 1. Create database tables
    try:
        async with async_engine.begin() as conn:
            # Test connection with SQLAlchemy 2.0 text()
            result = await conn.execute(text("SELECT 1"))
            print(f"✅ Database test: {result.scalar()}")
            
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    
    # 2. Create demo user
    async with AsyncSessionLocal() as session:
        try:
            demo_user = await Database.initialize_demo_user(session)
            if demo_user:
                print(f"✅ Demo user created: {demo_user.username}")
            else:
                print("✅ Demo user already exists")
        except Exception as e:
            print(f"⚠️  Demo user error: {e}")
    
    # 3. Load ML model
    try:
        model = get_model()
        print(f"✅ ML model loaded: {model.__class__.__name__}")
    except Exception as e:
        print(f"❌ ML model loading failed: {e}")
        raise
    
    print("\n" + "="*50)
    print("🌱 Plant Disease API Ready!")
    print("📚 Docs: http://localhost:8000/docs")
    print("🏃‍♂️ Server: http://localhost:8000")
    print("🔍 Health: http://localhost:8000/health")
    print("="*50 + "\n")
    
    yield  # App runs here
    
    # Shutdown
    print("🛑 Shutting down...")
    await async_engine.dispose()
    print("✅ Database connections closed")

# Create FastAPI app
app = FastAPI(
    title="Plant Disease API",
    description="Plant disease detection from leaf images",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# FIXED CORS Configuration
# Note: allow_credentials=True with allow_origins=["*"] is not allowed
# For development, use allow_origins=["*"] without credentials
# For production, specify exact origins with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - change to specific origins in production
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(history.router)
app.include_router(admin.router)

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Plant Disease Detection API",
        "version": "2.0.0",
        "status": "running",
        "docs": "http://localhost:8000/docs",
        "health_check": "http://localhost:8000/health",
        "timestamp": datetime.utcnow().isoformat()
    }

# Enhanced health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint with database verification"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {"connected": False},
        "model": {"loaded": False},
        "filesystem": {"writable": False}
    }
    
    # Check database
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            db_version = result.scalar()
            
            result = await conn.execute(text("SELECT 1"))
            db_test = result.scalar()
            
            health_status["database"] = {
                "connected": True,
                "version": db_version,
                "test_query": db_test == 1
            }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = {
            "connected": False,
            "error": str(e)
        }
    
    # Check model
    try:
        model = get_model()
        health_status["model"] = {
            "loaded": model is not None,
            "type": model.__class__.__name__ if model else None
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["model"] = {
            "loaded": False,
            "error": str(e)
        }
    
    # Check filesystem
    try:
        test_file = Path("data/images/.test")
        test_file.touch()
        test_file.unlink()
        health_status["filesystem"] = {
            "writable": True,
            "path": "data/images"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["filesystem"] = {
            "writable": False,
            "error": str(e)
        }
    
    return health_status

@app.get("/info", tags=["Info"])
async def api_info():
    """API information"""
    return {
        "name": "Plant Disease Detection API",
        "version": "2.0.0",
        "description": "Detect plant diseases from leaf images",
        "features": [
            "Authentication (JWT)",
            "Image upload and prediction",
            "Prediction history",
            "Admin dashboard",
            "SQLAlchemy 2.0 async database"
        ],
        "database": "PostgreSQL + SQLAlchemy 2.0",
        "ml_framework": "TensorFlow",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/auth",
            "predict": "/predict",
            "history": "/history",
            "admin": "/admin"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Add a simple test endpoint for debugging
@app.get("/test/cors", tags=["Debug"])
async def test_cors():
    """Test endpoint to verify CORS is working"""
    return {
        "message": "CORS is working if you can see this from your frontend",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"  # Changed from "warning" to "info" for better debugging
    )