from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Validation patterns
USERNAME_PATTERN = r"^[a-zA-Z0-9_]{3,50}$"

class LoginRequest(BaseModel):
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "password": "securepass123"
            }
        }
    }
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)

class RegisterRequest(BaseModel):
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "password": "securepass123",
                "email": "john@example.com"
            }
        }
    }
    username: str = Field(min_length=3, max_length=50, pattern=USERNAME_PATTERN)
    password: str = Field(min_length=6, max_length=128)  # Removed regex pattern - causes issues with special chars
    email: Optional[EmailStr] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str

class PredictionResponse(BaseModel):
    label: str
    confidence: float
    plant_type: str
    disease_name: str
    description: str
    treatment: str
    severity: str
    timestamp: str

class HistoryItem(BaseModel):
    prediction_id: str
    label: str
    confidence: float
    plant_type: str
    disease_name: str
    timestamp: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    region: Optional[str] = None
    city: Optional[str] = None

class StatsResponse(BaseModel):
    total_predictions: int
    healthy_count: int
    diseased_count: int
    most_common_disease: Optional[str]

class UserResponse(BaseModel):
    username: str
    user_id: str
    email: str
    created_at: str

class UsersListResponse(BaseModel):
    total_users: int
    users: List[UserResponse]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    checks: dict

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None