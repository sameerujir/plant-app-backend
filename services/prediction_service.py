import numpy as np
from PIL import Image
import io
from datetime import datetime
import tensorflow as tf
import tf_keras as keras
import gc
from sqlalchemy.ext.asyncio import AsyncSession
from config.settings import CLASS_NAMES, DISEASE_INFO
from utils.image_processor import preprocess_image
from utils.model_loader import get_model
from models.postgres_models import Prediction, Image as ImageModel
from models.database import Database

class PredictionService:
    def __init__(self):
        self.model = get_model()
    
    def reset_model_state(self):
        """Collect garbage - do NOT call clear_session() as it destroys loaded weights"""
        gc.collect()
    
    def parse_prediction_label(self, label: str) -> tuple:
        """Parse prediction label into plant type and disease name.

        Handles formats:
          - 'Early_Blight_Tomato'     -> ('Tomato', 'Early Blight')
          - 'Corn___Common_rust'       -> ('Corn', 'Common rust')
          - 'Potato___healthy'         -> ('Potato', 'healthy')
          - 'Tomato_healthy'           -> ('Tomato', 'healthy')
          - 'Pepper__bell___healthy'   -> ('Pepper bell', 'healthy')
        """
        # Format 1: triple-underscore separator
        if '___' in label:
            parts = label.split('___')
            plant_type = parts[0].replace('_', ' ').strip()
            disease_name = parts[1].replace('_', ' ').strip()
            return plant_type, disease_name

        # Format 2: PlantName at end e.g. Early_Blight_Tomato
        KNOWN_PLANTS = ['Tomato', 'Cauliflower', 'Corn', 'Potato', 'Pepper']
        for plant in KNOWN_PLANTS:
            if label.endswith(f'_{plant}'):
                disease_part = label[:-(len(plant) + 1)]
                return plant, disease_part.replace('_', ' ').strip()
            if label == plant or label.startswith(f'{plant}_'):
                rest = label[len(plant):].lstrip('_')
                return plant, rest.replace('_', ' ').strip() if rest else 'healthy'

        return "Unknown", label.replace('_', ' ')
    
    def get_disease_info(self, label: str) -> dict:
        """Get disease information from settings"""
        if label in DISEASE_INFO:
            return DISEASE_INFO[label]
        if 'healthy' in label.lower():
            return {
                'description': 'Plant appears healthy with no visible disease symptoms.',
                'treatment': 'Continue regular care and monitoring.',
                'severity': 'None'
            }
        return {
            'description': 'Disease detected. Consult a plant pathologist for accurate diagnosis.',
            'treatment': 'Isolate affected plants, avoid overhead watering, and consult an agricultural expert.',
            'severity': 'Unknown'
        }
    
    async def save_image_metadata(self, user_id: int, file_content: bytes, prediction_id: str, db: AsyncSession):
        """Save image metadata to database"""
        import uuid
        from pathlib import Path
        
        # Generate unique filename
        filename = f"{prediction_id}.jpg"
        # Save to local folder
        image_path = f"data/images/{filename}"
        
        # Ensure directory exists
        Path("data/images").mkdir(parents=True, exist_ok=True)
        
        # Save image
        try:
            with open(image_path, "wb") as f:
                f.write(file_content)
        except Exception as e:
            raise Exception(f"Failed to save image file: {str(e)}")
        
        # Create image record
        image_record = ImageModel(
            id=uuid.uuid4(),
            user_id=user_id,
            prediction_id=prediction_id,
            file_path=image_path,
            original_filename=filename,
            file_size_bytes=len(file_content)
        )
        
        db.add(image_record)
        await db.flush()  # Get the ID without committing
        
        return image_record.id, image_path
    
    async def predict_disease(
        self, 
        file_content: bytes, 
        username: str, 
        location: dict = None, 
        db: AsyncSession = None
    ) -> dict:
        """
        Main prediction function
        
        Args:
            file_content: Image file bytes
            username: Username of the user making prediction
            location: Optional location data dict
            db: Database session
            
        Returns:
            dict: Prediction results with disease info
            
        Raises:
            ValueError: For client errors (invalid image, etc.)
            Exception: For server errors (model issues, etc.)
        """
        try:
            # 1. Validate inputs
            if not file_content:
                raise ValueError("No file content provided")
            
            if len(file_content) == 0:
                raise ValueError("Empty file received")
            
            if db is None:
                raise ValueError("Database session is required")
            
            # 2. Reset model state for clean prediction
            self.reset_model_state()
            
            if self.model is None:
                raise Exception("Model not loaded - server may be starting up. Please try again.")

            # 3. Process image
            try:
                image = Image.open(io.BytesIO(file_content))
                
                # Validate image
                if image.size[0] < 50 or image.size[1] < 50:
                    raise ValueError("Image too small. Minimum size is 50x50 pixels")
                
                # Convert to RGB
                image = image.convert('RGB')
                
            except Exception as e:
                if isinstance(e, ValueError):
                    raise
                raise ValueError(f"Invalid image file: {str(e)}")
            
            # 4. Preprocess and predict
            try:
                processed_image = preprocess_image(image)
                predictions = self.model(processed_image, training=False)
                predicted_class_idx = np.argmax(predictions[0])
                confidence = float(predictions[0][predicted_class_idx])
            except Exception as e:
                raise Exception(f"Model prediction failed: {str(e)}")
            
            # 5. Parse results
            if predicted_class_idx >= len(CLASS_NAMES):
                raise Exception(f"Invalid prediction index: {predicted_class_idx}")
            
            predicted_label = CLASS_NAMES[predicted_class_idx]
            plant_type, disease_name = self.parse_prediction_label(predicted_label)
            disease_info = self.get_disease_info(predicted_label)
            
            # 6. Generate prediction ID and timestamp
            prediction_id = f"pred-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            timestamp = datetime.now().isoformat()
            
            # 7. Get user from database
            user = await Database.get_user(username, db)
            if not user:
                raise Exception(f"User not found: {username}")
            
            # 8. Save image metadata
            try:
                image_id, image_path = await self.save_image_metadata(
                    user.id, 
                    file_content, 
                    prediction_id, 
                    db
                )
            except Exception as e:
                raise Exception(f"Failed to save image: {str(e)}")
            
            # 9. Create prediction record
            prediction_data = {
                "prediction_id": prediction_id,
                "user_id": user.id,
                "label": predicted_label,
                "confidence": confidence,
                "plant_type": plant_type,
                "disease_name": disease_name,
                "latitude": location.get("latitude") if location else None,
                "longitude": location.get("longitude") if location else None,
                "country_code": location.get("country_code") if location else None,
                "region": location.get("region") if location else None,
                "city": location.get("city") if location else None,
                "timezone": location.get("timezone") if location else None,
                "location_relevant": bool(location),
                "created_at": datetime.fromisoformat(timestamp)
            }
            
            try:
                prediction = await Database.save_prediction(prediction_data, db)
            except Exception as e:
                raise Exception(f"Failed to save prediction to database: {str(e)}")
            
            # 10. Return results
            return {
                "label": predicted_label,
                "confidence": confidence,
                "plant_type": plant_type,
                "disease_name": disease_name,
                "description": disease_info['description'],
                "treatment": disease_info['treatment'],
                "severity": disease_info['severity'],
                "timestamp": timestamp,
                "image_url": f"/api/images/{image_id}",
                "location_relevant": bool(location),
                "regional_prevalence": "High" if location else "Unknown",
                "seasonal_risk": "Medium" if location else "Unknown",
            }
            
        except ValueError as e:
            # Client errors - don't clear session
            raise ValueError(str(e))
        except Exception as e:
            # Server errors
            gc.collect()
            raise Exception(f"Prediction error: {str(e)}")