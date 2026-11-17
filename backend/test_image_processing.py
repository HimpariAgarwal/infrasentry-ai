
from pathlib import Path
from image_processing.processor import process_image

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"

images = []

for extension in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
    images.extend(UPLOAD_DIR.rglob(extension))

if not images:
    print("No uploaded images found.")
    print("Upload a road damage image before running this test.")
else:

    image_path = images[0]

    print("\nStarting image processing...")
    print("Input image:", image_path.name)

    try:
        result = process_image(str(image_path))

        print("\nIMAGE PROCESSING SUCCESSFUL")

        for key, value in result.items():
            print(f"{key}: {value}")

    except Exception as error:
        print("\nIMAGE PROCESSING FAILED")
        print("Error:", error)
