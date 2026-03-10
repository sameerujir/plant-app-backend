# routers/predict.py - ENHANCED VERSION
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import json
from config.database import get_async_db
from config.security import get_current_user
from models.schemas import PredictionResponse
from services.prediction_service import PredictionService

router = APIRouter(prefix="/predict", tags=["prediction"])
prediction_service = PredictionService()

@router.post("/", response_model=PredictionResponse)
async def predict_disease(
    file: UploadFile = File(...),
    location_data: str = None,
    username: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Predict plant disease from uploaded image
    
    - **file**: Image file (JPEG, PNG, etc.) - Max 10MB
    - **location_data**: Optional JSON string with location info
    - Returns prediction with confidence, disease info, and treatment
    """
    
    # 1. Validate filename exists
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    # 2. Validate file type
    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to determine file type"
        )
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}. Must be an image (JPEG, PNG, etc.)"
        )
    
    # 3. Read and validate file size
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    try:
        contents = await file.read()
        
        # Check if file is empty
        if len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )
        
        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image too large ({len(contents) // (1024*1024)}MB). Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # 4. Parse location data if provided
        location = None
        if location_data:
            try:
                location = json.loads(location_data)
                # Validate location data structure
                if not isinstance(location, dict):
                    raise ValueError("Location data must be a JSON object")
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid location data format: {str(e)}"
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        
        # 5. Make prediction
        try:
            result = await prediction_service.predict_disease(
                contents, 
                username, 
                location, 
                db
            )
            return PredictionResponse(**result)
            
        except ValueError as e:
            # Client errors (invalid image, etc.)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            # Server errors (model issues, database issues, etc.)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Prediction failed: {str(e)}"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        # Always close the file
        await file.close()

@router.get("/test", tags=["Debug"])
async def test_predict_endpoint(username: str = Depends(get_current_user)):
    """Test endpoint to verify prediction route is accessible"""
    return {
        "message": "Prediction endpoint is accessible",
        "authenticated_user": username,
        "endpoint": "/predict/",
        "method": "POST",
        "required_params": {
            "file": "Image file (multipart/form-data)",
            "location_data": "Optional JSON string"
        }
    }