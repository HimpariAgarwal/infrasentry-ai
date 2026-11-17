
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(tags=["Image Upload"])

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/images/upload/{report_id}")
async def upload_report_image(
    report_id: str,
    file: UploadFile = File(...)
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed."
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid image content type."
        )

    # Read at most 5 MB + 1 byte to detect oversized uploads.
    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must not exceed 5 MB."
        )

    # Generate a safe filename instead of trusting the user's filename.
    filename = f"{uuid.uuid4().hex}{extension}"

    # Keep each report's images in its own directory.
    safe_report_id = "".join(
        character for character in report_id
        if character.isalnum() or character in "-_"
    )

    if not safe_report_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid report ID."
        )

    report_directory = UPLOAD_DIR / safe_report_id
    report_directory.mkdir(parents=True, exist_ok=True)

    file_path = report_directory / filename

    try:
        file_path.write_bytes(content)
    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Could not save the uploaded image."
        )

    return {
        "message": "Image uploaded successfully.",
        "report_id": report_id,
        "filename": filename,
        "image_url": f"/uploads/{safe_report_id}/{filename}",
        "size_bytes": len(content)
    }
