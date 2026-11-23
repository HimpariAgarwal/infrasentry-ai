from pathlib import Path
import json
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "data/processed/yolo_runs/baseline_v1/weights/best.pt"
DATA = ROOT / "data/processed/rdd2022_yolo/data.yaml"
OUTPUT = ROOT / "data/processed/yolo_runs"

if not MODEL.exists():
    raise FileNotFoundError(f"Checkpoint missing: {MODEL}")

model = YOLO(str(MODEL))

print("\nEvaluating best checkpoint on validation dataset...")

metrics = model.val(
    data=str(DATA),
    imgsz=416,
    batch=2,
    device="cpu",
    workers=0,
    plots=True,
    project=str(OUTPUT),
    name="baseline_eval",
    exist_ok=True
)

report = {
    "model": "YOLO26n",
    "checkpoint": str(MODEL),
    "mAP50": float(metrics.box.map50),
    "mAP50_95": float(metrics.box.map),
    "precision": float(metrics.box.mp),
    "recall": float(metrics.box.mr)
}

report_path = OUTPUT / "baseline_eval" / "evaluation_metrics.json"
report_path.write_text(json.dumps(report, indent=4), encoding="utf-8")

print("\nEVALUATION COMPLETE")
print(json.dumps(report, indent=4))
print("\nSaved:", report_path)
