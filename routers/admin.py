from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from config.database import get_async_db, async_engine  # Add async_engine import
from config.security import get_current_user
from models.schemas import (
    UsersListResponse, 
    UserResponse,
    StatsResponse,
    HistoryItem
)
from models.postgres_models import User, Prediction
from services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["admin"])
user_service = UserService()

async def verify_admin(
    username: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """Verify if user has admin privileges"""
    from sqlalchemy import select
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not getattr(user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return user

# ... rest of the admin.py code remains the same, but fix the health endpoint:

@router.get("/system/health")
async def system_health_check(
    admin_user: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """System health check with detailed information (admin only)"""
    from sqlalchemy import text
    import psutil
    import os
    
    # Database health
    db_status = "healthy"
    db_error = None
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            db_test = result.scalar()
            if db_test != 1:
                db_status = "unhealthy"
                db_error = "Database test query failed"
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Process metrics
    process = psutil.Process(os.getpid())
    
    # Counts
    users_count = await user_service.count_users(db)
    predictions_count = await user_service.count_predictions(db)
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "status": db_status,
            "error": db_error
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_usage_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2)
        },
        "application": {
            "process_memory_mb": round(process.memory_info().rss / (1024**2), 2),
            "process_threads": process.num_threads(),
            "process_cpu_percent": process.cpu_percent(),
            "uptime_seconds": round(process.create_time())
        },
        "counts": {
            "total_users": users_count,
            "total_predictions": predictions_count
        }
    }