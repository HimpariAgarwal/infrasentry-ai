from pathlib import Path
from tempfile import NamedTemporaryFile
from time import perf_counter
import os

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from PIL import Image
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "data" / "processed" / "yolo_runs" / "baseline_v1" / "weights" / "best.pt"

router = APIRouter(prefix="/api/v1", tags=["AI Detection"])

_model = None
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_model():
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise RuntimeError(f"YOLO checkpoint not found: {MODEL_PATH}")
        _model = YOLO(str(MODEL_PATH))

    return _model


def run_detection(image_path: Path, confidence: float = 0.10):
    model = get_model()

    start = perf_counter()

    result = model.predict(
        source=str(image_path),
        imgsz=416,
        conf=confidence,
        device="cpu",
        verbose=False
    )[0]

    elapsed_ms = (perf_counter() - start) * 1000
    names = model.names
    detections = []

    for box in result.boxes:
        class_id = int(box.cls[0].item())
        detections.append({
            "class_id": class_id,
            "damage_type": str(names[class_id]),
            "confidence": round(float(box.conf[0].item()), 4),
            "bounding_box": [
                round(float(value), 2)
                for value in box.xyxy[0].tolist()
            ]
        })

    return {
        "detections": detections,
        "detections_count": len(detections),
        "inference_time_ms": round(elapsed_ms, 2)
    }


@router.get("/model-info")
def model_info():
    model = get_model()
    names = model.names

    classes = (
        {str(k): str(v) for k, v in names.items()}
        if isinstance(names, dict)
        else {str(i): str(v) for i, v in enumerate(names)}
    )

    return {
        "model": "YOLO26n",
        "task": "road_damage_detection",
        "device": "CPU",
        "classes": classes,
        "checkpoint_available": MODEL_PATH.exists()
    }


@router.post("/detect")
async def detect_road_damage(
    file: UploadFile = File(...),
    confidence: float = Query(0.10, ge=0.01, le=1.0)
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Upload JPG, JPEG, PNG or WEBP image."
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Maximum image size is 10 MB.")

    temp_path = None

    try:
        with NamedTemporaryFile(suffix=extension, delete=False) as temp:
            temp.write(content)
            temp_path = Path(temp.name)

        with Image.open(temp_path) as image:
            image.verify()

        with Image.open(temp_path) as image:
            width, height = image.size

        output = run_detection(temp_path, confidence)

        return {
            "success": True,
            "filename": file.filename,
            "model": "YOLO26n",
            "image_width": width,
            "image_height": height,
            "confidence_threshold": confidence,
            **output,
            "message": (
                "Detection completed."
                if output["detections_count"] > 0
                else "No objects detected at this confidence threshold. "
                     "This baseline model is experimental."
            )
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Image processing failed: {str(exc)}"
        )
    finally:
        await file.close()
        if temp_path and temp_path.exists():
            os.unlink(temp_path)
