# services/auth_service.py - UPDATE
from fastapi import HTTPException, status, Depends
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config.database import get_async_db
from config.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from config.security import hash_password, verify_password, create_access_token
from models.postgres_models import User
from models.database import Database
from models.schemas import LoginRequest, RegisterRequest, LoginResponse

class AuthService:
    # Remove __init__ method if you have it
    
    async def login(self, request: LoginRequest, db: AsyncSession) -> LoginResponse:
        user = await Database.get_user(request.username, db)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return LoginResponse(
            access_token=access_token,
            user_id=user.user_id,
            username=user.username
        )

    async def register(self, request: RegisterRequest, db: AsyncSession) -> LoginResponse:
        # Check if user exists
        existing_user = await Database.get_user(request.username, db)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create user
        import time
        user_data = {
            "username": request.username,
            "hashed_password": hash_password(request.password),
            "user_id": f"user-{int(time.time())}",
            "email": request.email,
        }
        
        user = await Database.create_user(user_data, db)
        
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return LoginResponse(
            access_token=access_token,
            user_id=user.user_id,
            username=user.username
        )