# models/postgres_models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from config.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    user_id = Column(String(50), unique=True, nullable=False)
    email = Column(String(100))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Prediction data
    label = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    plant_type = Column(String(100), nullable=False)
    disease_name = Column(String(100), nullable=False)
    
    # Location data
    latitude = Column(Float)
    longitude = Column(Float)
    country_code = Column(String(10))
    region = Column(String(100))
    city = Column(String(100))
    timezone = Column(String(50))
    
    # Location insights
    location_relevant = Column(Boolean, default=False)
    regional_prevalence = Column(String(20))
    seasonal_risk = Column(String(20))
    local_recommendations = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Image(Base):
    __tablename__ = "images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    prediction_id = Column(String(50), index=True)
    
    # File storage
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255))
    file_size_bytes = Column(Integer)
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())