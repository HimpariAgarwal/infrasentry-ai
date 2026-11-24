import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.api_route_inventory import scan_api_routes


def build_inventory_report(source_root):
    result = scan_api_routes(source_root)

    method_counts = dict(sorted(
        Counter(
            route["method"] for route in result["routes"]
        ).items()
    ))

    files_with_routes = sorted({
        route["file"] for route in result["routes"]
    })

    return {
        "schema_version": "1.0",
        "summary": {
            "passed": result["passed"],
            "checked_files": result["checked_files"],
            "total_routes": result["route_count"],
            "files_with_routes": len(files_with_routes),
            "duplicate_candidates": len(result["duplicates"]),
            "parsing_errors": len(result["errors"]),
        },
        "methods": method_counts,
        "files": files_with_routes,
        "routes": result["routes"],
        "duplicates": result["duplicates"],
        "errors": result["errors"],
    }


def write_inventory_report(source_root, output_path):
    report = build_inventory_report(source_root)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = output_path.with_suffix(
        output_path.suffix + ".tmp"
    )

    temporary_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    temporary_path.replace(output_path)
    return report


def main():
    backend = ROOT / "backend"
    output = backend / "logs" / "api_route_inventory.json"

    print("\nINFRA SENTRY AI - API INVENTORY REPORT")
    print("=" * 48)

    try:
        report = write_inventory_report(backend, output)
    except (OSError, ValueError, SyntaxError) as exc:
        print(f"REPORT GENERATION FAILED: {exc}")
        return 1

    summary = report["summary"]

    print(f"Files scanned: {summary['checked_files']}")
    print(f"Total routes: {summary['total_routes']}")
    print(f"Files with routes: {summary['files_with_routes']}")
    print(f"Duplicate candidates: {summary['duplicate_candidates']}")

    print("\nHTTP method distribution:")
    for method, count in report["methods"].items():
        print(f"{method}: {count}")

    print(f"\nJSON report saved: {output}")

    if not summary["passed"]:
        print("Report contains Python parsing errors.")
        return 1

    print("\nAPI INVENTORY REPORT: GENERATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
