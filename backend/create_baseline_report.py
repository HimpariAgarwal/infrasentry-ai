from pathlib import Path
import csv
import json
import torch

root = Path(__file__).resolve().parents[1]
run = root / "data/processed/yolo_runs/baseline_v1"
weights = run / "weights"

checkpoint = torch.load(
    weights / "last.pt",
    map_location="cpu",
    weights_only=False
)

with open(run / "results.csv", newline="") as f:
    rows = list(csv.DictReader(f))

report = {
    "model": "YOLO26n",
    "dataset": "RDD2022",
    "classes": 4,
    "training_images": 5320,
    "validation_images": 1330,
    "completed_epochs": len(rows),
    "planned_epochs": 20,
    "checkpoint_epoch": checkpoint.get("epoch", -1) + 1,
    "best_checkpoint": str(weights / "best.pt"),
    "last_checkpoint": str(weights / "last.pt"),
    "latest_metrics": rows[-1] if rows else {}
}

output = run / "baseline_report.json"
output.write_text(json.dumps(report, indent=4), encoding="utf-8")

print(json.dumps(report, indent=4))
print("\nBASELINE REPORT SAVED:", output)
