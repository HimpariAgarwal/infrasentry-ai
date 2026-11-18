
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from uuid import uuid4

from image_processing.processor import process_image

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "processed"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/images/upload/{report_id}")
async def upload_image(
    report_id: str,
    file: UploadFile = File(...)
):
    safe_report_id = "".join(
        char for char in report_id
        if char.isalnum() or char in ("-", "_")
    )

    if not safe_report_id or safe_report_id != report_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid report ID."
        )

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image extension."
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid image content type."
        )

    contents = await file.read(MAX_FILE_SIZE + 1)

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Maximum image size is 5 MB."
        )

    report_folder = UPLOAD_DIR / safe_report_id
    report_folder.mkdir(parents=True, exist_ok=True)

    unique_filename = f"{uuid4().hex}{extension}"
    file_path = report_folder / unique_filename

    try:
        file_path.write_bytes(contents)
    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Could not save uploaded image."
        )

    try:
        processing_result = process_image(str(file_path))

        processed_filename = processing_result["processed_filename"]

        processing_result.pop("processed_path", None)

        processing_result["processed_image_url"] = (
            f"/images/processed/{processed_filename}"
        )

        processing_status = "completed"
        processing_error = None

    except Exception as error:
        processing_result = None
        processing_status = "failed"
        processing_error = str(error)

    return {
        "message": "Image uploaded successfully.",
        "report_id": safe_report_id,
        "original_filename": unique_filename,
        "original_image_url": f"/uploads/{safe_report_id}/{unique_filename}",
        "size_bytes": len(contents),
        "processing_status": processing_status,
        "processing_result": processing_result,
        "processing_error": processing_error
    }


@router.get("/images/processed/{filename}")
def get_processed_image(filename: str):

    # Prevent directory traversal
    if (
        not filename
        or Path(filename).name != filename
        or not filename.lower().endswith("_processed.jpg")
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid processed image filename."
        )

    image_path = PROCESSED_DIR / filename

    if not image_path.exists() or not image_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Processed image not found."
        )

    return FileResponse(
        path=image_path,
        media_type="image/jpeg",
        filename=filename
    )


@router.get("/images/processed")
def list_processed_images():

    images = []

    for image_path in PROCESSED_DIR.glob("*_processed.jpg"):
        if image_path.is_file():
            images.append({
                "filename": image_path.name,
                "image_url": f"/images/processed/{image_path.name}"
            })

    return {
        "total_processed_images": len(images),
        "images": images
    }
