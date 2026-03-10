from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.database import Database
from models.postgres_models import Prediction

class HistoryService:
    async def get_user_history(self, username: str, db: AsyncSession, limit: int = 20) -> List[Dict[str, Any]]:
        predictions = await Database.get_user_predictions(username, limit,0, db)
        
        return [
            {
                "prediction_id": pred.prediction_id,
                "label": pred.label,
                "confidence": float(pred.confidence),
                "plant_type": pred.plant_type,
                "disease_name": pred.disease_name,
                "timestamp": pred.created_at.isoformat(),
                "latitude": pred.latitude,
                "longitude": pred.longitude,
                "region": pred.region,
                "city": pred.city,
            }
            for pred in predictions
        ]
    
    async def get_user_stats(self, username: str, db: AsyncSession) -> Dict[str, Any]:
        predictions = await Database.get_user_predictions(username, 1000,0, db)  # Get all for stats
        
        if not predictions:
            return {
                "total_predictions": 0,
                "healthy_count": 0,
                "diseased_count": 0,
                "most_common_disease": None
            }

        total = len(predictions)
        healthy = sum(1 for p in predictions if 'healthy' in p.label.lower())
        diseased = total - healthy

        diseases = [p.disease_name for p in predictions if 'healthy' not in p.label.lower()]
        most_common = max(set(diseases), key=diseases.count) if diseases else None

        return {
            "total_predictions": total,
            "healthy_count": healthy,
            "diseased_count": diseased,
            "most_common_disease": most_common
        }