
import cv2
import numpy as np
from pathlib import Path


PROCESSED_DIR = Path(__file__).resolve().parent.parent / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


SUPPORTED_FORMATS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


def process_image(image_path: str):

    image_path = Path(image_path)

    # 1. Check whether the file exists
    if not image_path.exists():
        raise FileNotFoundError("Image file does not exist.")

    # 2. Validate extension
    if image_path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError("Unsupported image format.")

    # 3. Read image
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError("Invalid or corrupted image.")

    # 4. Extract original dimensions
    original_height, original_width = image.shape[:2]

    if original_width == 0 or original_height == 0:
        raise ValueError("Invalid image dimensions.")

    # 5. Resize while maintaining aspect ratio
    target_size = 640

    scale = target_size / max(original_width, original_height)

    new_width = max(1, int(original_width * scale))
    new_height = max(1, int(original_height * scale))

    resized_image = cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
    )

    # 6. Convert BGR to RGB
    rgb_image = cv2.cvtColor(
        resized_image,
        cv2.COLOR_BGR2RGB
    )

    # 7. Normalize pixel values from 0-255 to 0-1
    normalized_image = (
        rgb_image.astype(np.float32) / 255.0
    )

    # 8. Save resized RGB image
    output_name = f"{image_path.stem}_processed.jpg"

    output_path = PROCESSED_DIR / output_name

    success = cv2.imwrite(
        str(output_path),
        cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR),
        [cv2.IMWRITE_JPEG_QUALITY, 95]
    )

    if not success:
        raise RuntimeError("Could not save processed image.")

    # 9. Return processing information
    return {
        "original_filename": image_path.name,
        "original_width": original_width,
        "original_height": original_height,
        "processed_width": new_width,
        "processed_height": new_height,
        "channels": 3,
        "format": image_path.suffix.lower(),
        "processed_filename": output_name,
        "processed_path": str(output_path),
        "normalized_min": float(normalized_image.min()),
        "normalized_max": float(normalized_image.max()),
        "normalization": "pixel values divided by 255.0",
        "processing_status": "completed"
    }
