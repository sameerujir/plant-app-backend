import numpy as np
from PIL import Image
import cv2

# Must match training configuration exactly
IMG_SIZE = 128
ASPECT_METHOD = 'pad'   # Training used ASPECT_RATIO_METHOD = 'pad'


def resize_with_pad(image_rgb: np.ndarray, target_size: int) -> np.ndarray:
    """
    Pad-then-resize to preserve aspect ratio.
    Matches training: ASPECT_RATIO_METHOD = 'pad'
    """
    h, w = image_rgb.shape[:2]

    if h > w:
        pad = (h - w) // 2
        image_rgb = cv2.copyMakeBorder(
            image_rgb, 0, 0, pad, pad,
            cv2.BORDER_CONSTANT, value=[0, 0, 0]
        )
    elif w > h:
        pad = (w - h) // 2
        image_rgb = cv2.copyMakeBorder(
            image_rgb, pad, pad, 0, 0,
            cv2.BORDER_CONSTANT, value=[0, 0, 0]
        )

    return cv2.resize(image_rgb, (target_size, target_size))


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Preprocess a PIL image for inference.

    Training pipeline:
      1. Convert BGR → RGB  (we receive RGB from PIL already)
      2. Pad to square, then resize to 128×128
      3. Normalize: pixel / 255.0   ← NO mobilenet_v2.preprocess_input
      4. Expand dims → (1, 128, 128, 3)
    """
    try:
        # Ensure RGB
        image = image.convert('RGB')
        image_np = np.array(image, dtype=np.uint8)

        # Pad + resize  (mirrors data_loader.resize_with_aspect_ratio)
        image_np = resize_with_pad(image_np, IMG_SIZE)

        # Normalize to [0, 1]  — matches: img.astype(np.float32) / 255.0
        image_np = image_np.astype(np.float32) / 255.0

        # Add batch dimension → (1, 128, 128, 3)
        return np.expand_dims(image_np, axis=0)

    except Exception as e:
        raise Exception(f"Image processing failed: {e}")