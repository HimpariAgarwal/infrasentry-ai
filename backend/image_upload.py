
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4

from image_processing.processor import process_image

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/images/upload/{report_id}")
async def upload_image(
    report_id: str,
    file: UploadFile = File(...)
):
    # Validate report ID
    safe_report_id = "".join(
        char for char in report_id
        if char.isalnum() or char in ("-", "_")
    )

    if not safe_report_id or safe_report_id != report_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid report ID."
        )

    # Validate filename extension
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed."
        )

    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid image content type."
        )

    # Read and validate file size
    contents = await file.read(MAX_FILE_SIZE + 1)

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 5 MB."
        )

    # Create report-specific upload folder
    report_folder = UPLOAD_DIR / safe_report_id
    report_folder.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename
    unique_filename = f"{uuid4().hex}{extension}"
    file_path = report_folder / unique_filename

    # Save original image
    try:
        file_path.write_bytes(contents)
    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Could not save uploaded image."
        )

    # Automatically process the uploaded image
    try:
        processing_result = process_image(str(file_path))

        # Do not expose the server's absolute file path
        processing_result.pop("processed_path", None)

        processing_status = "completed"
        processing_error = None

    except Exception as error:
        processing_result = None
        processing_status = "failed"
        processing_error = str(error)

    return {
        "message": "Image uploaded successfully.",
        "report_id": safe_report_id,
        "filename": unique_filename,
        "image_url": f"/uploads/{safe_report_id}/{unique_filename}",
        "size_bytes": len(contents),
        "processing_status": processing_status,
        "processing_result": processing_result,
        "processing_error": processing_error
    }
