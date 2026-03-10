import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "insecure-dev-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
MODEL_PATH = os.getenv("MODEL_PATH", "data/mobilenetv2_final_model.keras")


ARGON2_CONFIG = {
    "time_cost": 2,
    "memory_cost": 65536,
    "parallelism": 1,
    "hash_len": 32,
    "salt_len": 16
}

CORS_ORIGINS = ["*"]

CLASS_NAMES = [
    'Bacterial_Wilt_Tomato',       # 0
    'Black_Rot_Cauliflower',        # 1
    'Blossom_End_Rot_Tomato',       # 2
    'Corn___Common_rust',           # 3
    'Corn___healthy',               # 4
    'Downy_Mildew_Cauliflower',     # 5
    'Early_Blight_Tomato',          # 6
    'Late_Blight_Tomato',           # 7
    'Pepper__bell___healthy',       # 8
    'Potato___Late_blight',         # 9
    'Potato___healthy',             # 10
    'Powdery_Mildew_Tomato',        # 11
    'Septoria_Leaf_Tomato',         # 12
    'Tomato_healthy',               # 13
]

DISEASE_INFO = {
    'Bacterial_Wilt_Tomato': {
        'description': 'Bacterial disease causing rapid wilting of tomato plants due to vascular blockage.',
        'treatment': 'Remove and destroy infected plants immediately. Avoid overhead watering, rotate crops, and use resistant varieties. No chemical cure is effective once infected.',
        'severity': 'Critical'
    },
    'Black_Rot_Cauliflower': {
        'description': 'Bacterial disease causing V-shaped yellow lesions on leaf margins and blackening of veins.',
        'treatment': 'Remove infected leaves, apply copper-based bactericides, ensure good air circulation, and avoid wetting foliage. Practice crop rotation.',
        'severity': 'High'
    },
    'Blossom_End_Rot_Tomato': {
        'description': 'Physiological disorder caused by calcium deficiency, resulting in dark, sunken lesions at the blossom end of fruit.',
        'treatment': 'Maintain consistent soil moisture, apply calcium foliar sprays, and ensure proper soil pH (6.2–6.8). Avoid over-fertilizing with nitrogen.',
        'severity': 'Moderate'
    },
    'Corn___Common_rust': {
        'description': 'Fungal disease producing small, powdery, brick-red pustules on both leaf surfaces.',
        'treatment': 'Apply fungicides such as triazoles or strobilurins at early stages. Plant resistant hybrids and monitor fields regularly.',
        'severity': 'Moderate'
    },
    'Corn___healthy': {
        'description': 'Corn plant appears healthy with no visible disease symptoms.',
        'treatment': 'Continue regular care, ensure adequate fertilization, and monitor for early signs of pests or disease.',
        'severity': 'None'
    },
    'Downy_Mildew_Cauliflower': {
        'description': 'Fungal-like disease causing yellow patches on upper leaf surfaces and white-grey fuzzy growth on the underside.',
        'treatment': 'Apply appropriate fungicides (mancozeb or metalaxyl), improve air circulation, avoid overhead irrigation, and remove infected debris.',
        'severity': 'High'
    },
    'Early_Blight_Tomato': {
        'description': 'Fungal disease causing dark, concentric ring lesions (target-like spots) on older leaves first.',
        'treatment': 'Apply copper-based or chlorothalonil fungicides. Remove infected lower leaves, mulch soil to prevent spore splash, and rotate crops annually.',
        'severity': 'Moderate'
    },
    'Late_Blight_Tomato': {
        'description': 'Destructive fungal-like disease causing water-soaked, dark brown lesions on leaves, stems, and fruit.',
        'treatment': 'Apply copper-based or systemic fungicides immediately. Remove and destroy infected plant material. Ensure good drainage and avoid overhead watering.',
        'severity': 'Critical'
    },
    'Pepper__bell___healthy': {
        'description': 'Bell pepper plant appears healthy with no visible disease symptoms.',
        'treatment': 'Continue regular care, maintain consistent watering, and monitor for pests or nutrient deficiencies.',
        'severity': 'None'
    },
    'Potato___Late_blight': {
        'description': 'Devastating disease causing dark, water-soaked lesions on leaves and tubers, rapidly destroying entire crops.',
        'treatment': 'Apply protective fungicides (mancozeb, chlorothalonil) preventively. Destroy infected plant material, hill soil around plants, and use certified disease-free seed potatoes.',
        'severity': 'Critical'
    },
    'Potato___healthy': {
        'description': 'Potato plant appears healthy with no visible disease symptoms.',
        'treatment': 'Continue regular care, ensure proper hilling, and monitor for early blight or pest signs.',
        'severity': 'None'
    },
    'Powdery_Mildew_Tomato': {
        'description': 'Fungal disease producing white, powdery coating on leaf surfaces, causing yellowing and leaf drop.',
        'treatment': 'Apply sulfur-based or potassium bicarbonate fungicides. Improve air circulation and avoid excessive nitrogen fertilization.',
        'severity': 'Moderate'
    },
    'Septoria_Leaf_Tomato': {
        'description': 'Fungal disease causing small, circular spots with dark borders and light centers, leading to leaf yellowing and defoliation.',
        'treatment': 'Remove infected leaves, apply copper or chlorothalonil fungicides, mulch soil to prevent spore splash, and avoid overhead watering.',
        'severity': 'Moderate'
    },
    'Tomato_healthy': {
        'description': 'Tomato plant appears healthy with no visible disease symptoms.',
        'treatment': 'Continue regular care, maintain consistent watering, and monitor for early signs of disease or pests.',
        'severity': 'None'
    },
}
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://planta_user:plant123secure@localhost/plantcare_db"
)