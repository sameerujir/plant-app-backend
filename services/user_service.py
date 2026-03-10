from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.postgres_models import User, Prediction, Image
from models.database import Database  # For getting user info

class UserService:
    async def list_users(self, db: AsyncSession) -> Dict[str, Any]:
        """List all users"""
        # Get users from Database class
        users = await Database.get_all_users(db)
        
        user_list = [
            {
                "username": user.username,
                "user_id": user.user_id,
                "email": user.email or "",
                "created_at": user.created_at.isoformat() if user.created_at else "N/A",
                "is_admin": getattr(user, 'is_admin', False)  # Use getattr for safety
            }
            for user in users
        ]
        
        return {
            "total_users": len(users),
            "users": user_list
        }
    
    async def delete_user(self, username: str, db: AsyncSession) -> bool:
        """Delete user and all their data"""
        # Get user using Database class
        user = await Database.get_user(username, db)
        
        if not user:
            return False
        
        # First, delete user's images
        img_result = await db.execute(
            select(Image).where(Image.user_id == user.id)
        )
        images = img_result.scalars().all()
        for image in images:
            await db.delete(image)
        
        # Then, delete user's predictions
        pred_result = await db.execute(
            select(Prediction).where(Prediction.user_id == user.id)
        )
        predictions = pred_result.scalars().all()
        for prediction in predictions:
            await db.delete(prediction)
        
        # Finally, delete the user
        await db.delete(user)
        await db.commit()
        
        return True
    
    async def get_user_stats(self, username: str, db: AsyncSession) -> Dict[str, Any]:
        """Get user statistics"""
        user = await Database.get_user(username, db)
        
        if not user:
            return {}
        
        # Get predictions count
        pred_result = await db.execute(
            select(Prediction)
            .where(Prediction.user_id == user.id)
        )
        predictions = pred_result.scalars().all()
        
        # Get images count
        img_result = await db.execute(
            select(Image)
            .where(Image.user_id == user.id)
        )
        images = img_result.scalars().all()
        
        return {
            "username": user.username,
            "user_id": user.user_id,
            "total_predictions": len(predictions),
            "total_images": len(images),
            "account_created": user.created_at.isoformat() if user.created_at else "N/A",
            "last_login": "N/A"  # Add last_login field to User model if needed
        }
    
    async def count_users(self, db: AsyncSession) -> int:
        """Count total users"""
        result = await db.execute(
            select(func.count(User.id))
        )
        return result.scalar() or 0
    
    async def count_predictions(self, db: AsyncSession) -> int:
        """Count total predictions"""
        result = await db.execute(
            select(func.count(Prediction.id))
        )
        return result.scalar() or 0
    
    async def get_user_by_id(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Get user by user_id"""
        user = await Database.get_user_by_id(user_id, db)
        
        if not user:
            return {}
        
        return {
            "username": user.username,
            "user_id": user.user_id,
            "email": user.email or "",
            "created_at": user.created_at.isoformat() if user.created_at else "N/A",
            "is_admin": getattr(user, 'is_admin', False)
        }
    
    async def get_users_paginated(
        self, 
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get users with pagination"""
        result = await db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        users = result.scalars().all()
        
        user_list = [
            {
                "username": user.username,
                "user_id": user.user_id,
                "email": user.email or "",
                "created_at": user.created_at.isoformat() if user.created_at else "N/A",
                "is_admin": getattr(user, 'is_admin', False)
            }
            for user in users
        ]
        
        total = await self.count_users(db)
        
        return {
            "users": user_list,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total
        }