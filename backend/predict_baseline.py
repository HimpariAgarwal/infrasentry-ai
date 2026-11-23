from pathlib import Path
from ultralytics import YOLO
import json

ROOT = Path(__file__).resolve().parents[1]

MODEL = ROOT / "data/processed/yolo_runs/baseline_v1/weights/best.pt"
IMAGE_DIR = ROOT / "data/processed/rdd2022_yolo/images/val"
OUTPUT = ROOT / "data/processed/yolo_runs"

images = sorted(IMAGE_DIR.glob("*.jpg"))[:8]

if not images:
    raise FileNotFoundError(f"No validation images found: {IMAGE_DIR}")

model = YOLO(str(MODEL))

results = model.predict(
    source=[str(p) for p in images],
    imgsz=416,
    conf=0.10,
    device="cpu",
    save=True,
    save_txt=True,
    save_conf=True,
    project=str(OUTPUT),
    name="baseline_predictions",
    exist_ok=True
)

report = []

for image_path, result in zip(images, results):
    count = len(result.boxes)
    report.append({
        "image": image_path.name,
        "detections": count
    })
    print(f"{image_path.name}: {count} detections")

report_path = OUTPUT / "baseline_predictions" / "prediction_report.json"
report_path.write_text(json.dumps(report, indent=4), encoding="utf-8")

print("\nPREDICTIONS COMPLETE")
print("Visual results:", OUTPUT / "baseline_predictions")
print("Report:", report_path)
