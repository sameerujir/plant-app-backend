# routers/history.py - UPDATE
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.database import get_async_db
from config.security import get_current_user
from models.schemas import HistoryItem, StatsResponse
from services.history_service import HistoryService

router = APIRouter(prefix="/history", tags=["history"])
history_service = HistoryService()

@router.get("/", response_model=List[HistoryItem])
async def get_history(
    username: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    return await history_service.get_user_history(username, db)

@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    username: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    return await history_service.get_user_stats(username, db)