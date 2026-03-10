from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import Optional, List
from models.postgres_models import User, Prediction

class Database:
    """PostgreSQL database operations with SQLAlchemy 2.0 patterns"""
    
    @staticmethod
    async def get_user(username: str, db: AsyncSession) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(user_id: str, db: AsyncSession) -> Optional[User]:
        """Get user by user_id"""
        result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(user_data: dict, db: AsyncSession) -> User:
        """Create new user"""
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def update_user(user: User, update_data: dict, db: AsyncSession) -> User:
        """Update user information"""
        for key, value in update_data.items():
            setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def delete_user(user: User, db: AsyncSession) -> bool:
        """Delete a user"""
        await db.delete(user)
        await db.commit()
        return True
    
    @staticmethod
    async def save_prediction(prediction_data: dict, db: AsyncSession) -> Prediction:
        """Save prediction to database"""
        prediction = Prediction(**prediction_data)
        db.add(prediction)
        await db.commit()
        await db.refresh(prediction)
        return prediction
    
    @staticmethod
    async def get_prediction(prediction_id: int, db: AsyncSession) -> Optional[Prediction]:
        """Get prediction by ID"""
        result = await db.execute(
            select(Prediction).where(Prediction.id == prediction_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_predictions(
        username: str, 
        limit: int = 20, 
        offset: int = 0,
        db: AsyncSession = None
    ) -> List[Prediction]:
        """Get user's prediction history with pagination"""
        if not db:
            raise ValueError("Database session (db) is required")
        
        return await Database._get_user_predictions_internal(username, limit, offset, db)
    
    @staticmethod
    async def _get_user_predictions_internal(
        username: str, 
        limit: int, 
        offset: int, 
        db: AsyncSession
    ) -> List[Prediction]:
        """Internal method to get user predictions"""
        # Get user first
        user = await Database.get_user(username, db)
        if not user:
            return []
        
        # Get predictions with pagination
        result = await db.execute(
            select(Prediction)
            .where(Prediction.user_id == user.id)
            .order_by(Prediction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    @staticmethod
    async def count_user_predictions(username: str, db: AsyncSession) -> int:
        """Count total predictions for a user"""
        user = await Database.get_user(username, db)
        if not user:
            return 0
        
        result = await db.execute(
            select(func.count(Prediction.id))
            .where(Prediction.user_id == user.id)
        )
        return result.scalar()
    
    @staticmethod
    async def get_recent_predictions(
        db: AsyncSession, 
        limit: int = 50
    ) -> List[Prediction]:
        """Get recent predictions from all users"""
        result = await db.execute(
            select(Prediction)
            .order_by(Prediction.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def search_predictions(
        search_term: str,
        db: AsyncSession,
        limit: int = 20
    ) -> List[Prediction]:
        """Search predictions by plant name or disease"""
        result = await db.execute(
            select(Prediction)
            .where(
                (Prediction.plant_name.ilike(f"%{search_term}%")) |
                (Prediction.disease_name.ilike(f"%{search_term}%"))
            )
            .order_by(Prediction.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_predictions_by_disease(
        disease_name: str,
        db: AsyncSession,
        limit: int = 20
    ) -> List[Prediction]:
        """Get predictions by specific disease"""
        result = await db.execute(
            select(Prediction)
            .where(Prediction.disease_name == disease_name)
            .order_by(Prediction.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def delete_prediction(prediction: Prediction, db: AsyncSession) -> bool:
        """Delete a prediction"""
        await db.delete(prediction)
        await db.commit()
        return True
    
    @staticmethod
    async def get_predictions_statistics(db: AsyncSession) -> dict:
        """Get statistics about predictions"""
        # Total predictions count
        total_result = await db.execute(
            select(func.count(Prediction.id))
        )
        total = total_result.scalar()
        
        # Unique diseases count
        diseases_result = await db.execute(
            select(func.count(func.distinct(Prediction.disease_name)))
        )
        unique_diseases = diseases_result.scalar()
        
        # Unique users with predictions
        users_result = await db.execute(
            select(func.count(func.distinct(Prediction.user_id)))
        )
        unique_users = users_result.scalar()
        
        # Today's predictions
        today = datetime.utcnow().date()
        today_result = await db.execute(
            select(func.count(Prediction.id))
            .where(func.date(Prediction.created_at) == today)
        )
        today_predictions = today_result.scalar()
        
        return {
            "total_predictions": total or 0,
            "unique_diseases": unique_diseases or 0,
            "unique_users": unique_users or 0,
            "today_predictions": today_predictions or 0
        }
    
    @staticmethod
    async def initialize_demo_user(db: AsyncSession) -> User:
        """Initialize demo user if not exists"""
        from config.security import hash_password
        
        result = await db.execute(
            select(User).where(User.username == "demo")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            demo_user = User(
                username="demo",
                hashed_password=hash_password("demo123"),
                user_id="demo-user-001",
                email="demo@plantdoctor.com",
                created_at=datetime.utcnow()
            )
            db.add(demo_user)
            await db.commit()
            await db.refresh(demo_user)
            print("✅ Demo user created in PostgreSQL")
            return demo_user
        
        return user

    @staticmethod
    async def initialize_admin_user(db: AsyncSession) -> Optional[User]:
        """Initialize admin user if not exists"""
        from config.security import hash_password
        
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            admin_user = User(
                username="admin",
                hashed_password=hash_password("admin123"),
                user_id="admin-user-001",
                email="admin@plantdoctor.com",
                is_admin=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)
            print("✅ Admin user created in PostgreSQL")
            return admin_user
        
        return user
    
    @staticmethod
    async def get_all_users(
        db: AsyncSession, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[User]:
        """Get all users with pagination"""
        result = await db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    @staticmethod
    async def count_users(db: AsyncSession) -> int:
        """Count total users"""
        result = await db.execute(
            select(func.count(User.id))
        )
        return result.scalar()
    
    @staticmethod
    async def get_user_statistics(username: str, db: AsyncSession) -> Optional[dict]:
        """Get statistics for a specific user"""
        user = await Database.get_user(username, db)
        if not user:
            return None
        
        # Total predictions by user
        total_result = await db.execute(
            select(func.count(Prediction.id))
            .where(Prediction.user_id == user.id)
        )
        total = total_result.scalar()
        
        # Unique diseases detected by user
        diseases_result = await db.execute(
            select(func.count(func.distinct(Prediction.disease_name)))
            .where(Prediction.user_id == user.id)
        )
        unique_diseases = diseases_result.scalar()
        
        # First prediction date
        first_result = await db.execute(
            select(func.min(Prediction.created_at))
            .where(Prediction.user_id == user.id)
        )
        first_prediction = first_result.scalar()
        
        # Latest prediction date
        latest_result = await db.execute(
            select(func.max(Prediction.created_at))
            .where(Prediction.user_id == user.id)
        )
        latest_prediction = latest_result.scalar()
        
        return {
            "username": username,
            "total_predictions": total or 0,
            "unique_diseases": unique_diseases or 0,
            "first_prediction": first_prediction.isoformat() if first_prediction else None,
            "latest_prediction": latest_prediction.isoformat() if latest_prediction else None,
            "account_created": user.created_at.isoformat() if user.created_at else None
        }