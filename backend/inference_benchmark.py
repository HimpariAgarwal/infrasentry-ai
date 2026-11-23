from pathlib import Path
import json
import statistics
from datetime import datetime, timezone
from ai_router import run_detection

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "data" / "processed" / "rdd2022_yolo" / "images" / "val"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

images = sorted(IMAGE_DIR.glob("*.jpg"))[:25]
if not images:
    raise SystemExit(f"No validation JPG images found: {IMAGE_DIR}")

results = []
errors = []

for image in images:
    try:
        output = run_detection(image)
        results.append({
            "image": image.name,
            "detections_count": output["detections_count"],
            "inference_time_ms": output["inference_time_ms"],
            "detections": output["detections"],
        })
        print(
            f'{image.name}: {output["detections_count"]} detections, '
            f'{output["inference_time_ms"]:.2f} ms'
        )
    except Exception as exc:
        errors.append({"image": image.name, "error": str(exc)})
        print(f"FAILED: {image.name}: {exc}")

times = [item["inference_time_ms"] for item in results]
counts = [item["detections_count"] for item in results]

report = {
    "project": "InfraSentry AI",
    "benchmark_date_utc": datetime.now(timezone.utc).isoformat(),
    "benchmark_type": "Inference performance only; not an accuracy evaluation",
    "images_attempted": len(images),
    "images_succeeded": len(results),
    "images_failed": len(errors),
    "total_detections": sum(counts),
    "images_with_detections": sum(1 for count in counts if count > 0),
    "images_without_detections": sum(1 for count in counts if count == 0),
    "average_inference_time_ms": round(statistics.mean(times), 2) if times else None,
    "median_inference_time_ms": round(statistics.median(times), 2) if times else None,
    "maximum_inference_time_ms": round(max(times), 2) if times else None,
    "minimum_inference_time_ms": round(min(times), 2) if times else None,
    "results": results,
    "errors": errors,
}

report_path = REPORT_DIR / "day21_inference_benchmark.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\nBENCHMARK SUMMARY")
print("Images attempted:", len(images))
print("Images successful:", len(results))
print("Images failed:", len(errors))
print("Total detections:", sum(counts))
print("Average inference:", report["average_inference_time_ms"], "ms")
print("Median inference:", report["median_inference_time_ms"], "ms")
print("Report:", report_path)

if not results:
    raise SystemExit("Benchmark produced no successful results.")
