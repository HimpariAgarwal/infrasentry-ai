from pathlib import Path
import argparse
import json
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "processed" / "rdd2022_yolo"
DATA_YAML = DATASET / "data.yaml"
MODEL = ROOT / "yolo26n.pt"
OUTPUT = ROOT / "data" / "processed" / "yolo_runs"


def parse_args():
    parser = argparse.ArgumentParser(
        description="InfraSentry AI YOLO baseline training"
    )
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--imgsz", type=int, default=416)
    parser.add_argument("--batch", type=int, default=2)
    parser.add_argument("--fraction", type=float, default=1.0)
    parser.add_argument("--name", type=str, default="baseline_v1")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()

    required_paths = [
        DATA_YAML,
        MODEL,
        DATASET / "images" / "train",
        DATASET / "images" / "val",
    ]

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(f"Required path missing: {path}")

    if not 0 < args.fraction <= 1:
        raise ValueError("fraction must be greater than 0 and at most 1")

    if args.epochs < 1 or args.imgsz < 32 or args.batch < 1:
        raise ValueError("Invalid training parameters")

    config = {
        "model": str(MODEL),
        "dataset": str(DATA_YAML),
        "epochs": args.epochs,
        "image_size": args.imgsz,
        "batch_size": args.batch,
        "fraction": args.fraction,
        "device": "cpu",
        "workers": 0,
        "seed": 42,
        "output": str(OUTPUT / args.name),
    }

    print("\nINFRA SENTRY AI - BASELINE CONFIGURATION")
    print(json.dumps(config, indent=4))

    if args.dry_run:
        print("\nDRY RUN SUCCESSFUL. No training started.")
        return

    model = YOLO(str(MODEL))

    model.train(
        data=str(DATA_YAML),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device="cpu",
        workers=0,
        fraction=args.fraction,
        seed=42,
        deterministic=True,
        pretrained=True,
        amp=False,
        plots=True,
        save=True,
        val=True,
        project=str(OUTPUT),
        name=args.name,
        exist_ok=False,
    )

    print("\nBASELINE TRAINING FINISHED.")
    print(f"Output directory: {OUTPUT / args.name}")


if __name__ == "__main__":
    main()
