from datetime import datetime

def get_current_timestamp() -> str:
    return datetime.now().isoformat()

def validate_image_size(image_data: bytes, max_size_mb: int = 10) -> bool:
    max_size_bytes = max_size_mb * 1024 * 1024
    return len(image_data) <= max_size_bytes