import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.api_route_inventory_report import build_inventory_report


def validate_documentation(report, markdown):
    routes = report.get("routes", [])
    methods = report.get("methods", {})

    missing_routes = []

    for route in routes:
        method = str(route.get("method", ""))
        path = str(route.get("path", ""))

        expected = f"| {method} | `{path}` |"

        if expected not in markdown:
            missing_routes.append({
                "method": method,
                "path": path,
            })

    missing_methods = []

    for method, count in methods.items():
        expected = f"| {method} | {count} |"

        if expected not in markdown:
            missing_methods.append(method)

    errors = []

    if missing_routes:
        errors.append("One or more discovered routes are missing.")

    if missing_methods:
        errors.append("HTTP method distribution does not match.")

    parsing_errors = report.get("summary", {}).get(
        "parsing_errors", 0
    )

    if parsing_errors:
        errors.append("Python parsing errors exist in the inventory.")

    return {
        "passed": not errors,
        "total_routes": len(routes),
        "missing_route_count": len(missing_routes),
        "missing_routes": missing_routes,
        "missing_methods": missing_methods,
        "parsing_errors": parsing_errors,
        "errors": errors,
    }


def write_validation_report(result, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **result,
    }

    temporary = output_path.with_suffix(output_path.suffix + ".tmp")

    temporary.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    temporary.replace(output_path)

    return output_path


def main():
    backend = ROOT / "backend"
    documentation = ROOT / "docs" / "generated_api_reference.md"
    output = (
        ROOT / "backend" / "logs"
        / "api_documentation_validation.json"
    )

    if not documentation.exists():
        print("Generated API documentation not found.")
        print("Run Day 97 generator first.")
        return 1

    report = build_inventory_report(backend)
    markdown = documentation.read_text(encoding="utf-8")

    result = validate_documentation(report, markdown)
    write_validation_report(result, output)

    print("\nAPI DOCUMENTATION INTEGRITY")
    print("=" * 45)
    print(f"Total routes: {result['total_routes']}")
    print(f"Missing routes: {result['missing_route_count']}")
    print(f"Missing methods: {len(result['missing_methods'])}")
    print(f"Parsing errors: {result['parsing_errors']}")
    print(f"Validation: {'PASS' if result['passed'] else 'FAIL'}")
    print(f"Report: {output}")

    for error in result["errors"]:
        print(f"ERROR: {error}")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
