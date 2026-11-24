import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.api_route_inventory_report import build_inventory_report


def escape_markdown(value):
    return str(value).replace("|", r"\|").replace("`", r"\`")


def generate_markdown(report):
    summary = report["summary"]
    routes = report["routes"]

    lines = [
        "# InfraSentry AI - API Reference",
        "",
        "Automatically generated static API route reference.",
        "",
        "## Summary",
        "",
        f"- Python files scanned: {summary['checked_files']}",
        f"- Total routes discovered: {summary['total_routes']}",
        f"- Files containing routes: {summary['files_with_routes']}",
        f"- Duplicate candidates: {summary['duplicate_candidates']}",
        f"- Parsing errors: {summary['parsing_errors']}",
        "",
        "## HTTP Method Distribution",
        "",
        "| Method | Route Count |",
        "|---|---:|",
    ]

    for method, count in sorted(report["methods"].items()):
        lines.append(f"| {escape_markdown(method)} | {count} |")

    lines.extend([
        "",
        "## Endpoints",
        "",
        "| Method | Endpoint | Function | Source File |",
        "|---|---|---|---|",
    ])

    for route in sorted(
        routes,
        key=lambda item: (item["path"], item["method"], item["file"])
    ):
        lines.append(
            f"| {escape_markdown(route['method'])} "
            f"| `{escape_markdown(route['path'])}` "
            f"| `{escape_markdown(route['function'])}` "
            f"| `{escape_markdown(route['file'])}` |"
        )

    lines.extend(["", "## Duplicate Route Candidates", ""])

    if report["duplicates"]:
        lines.extend([
            "| Method | Endpoint |",
            "|---|---|",
        ])

        for item in report["duplicates"]:
            lines.append(
                f"| {escape_markdown(item['method'])} "
                f"| `{escape_markdown(item['path'])}` |"
            )

        lines.extend([
            "",
            "These are static duplicate candidates. "
            "Review them manually; router prefixes may affect effective paths.",
        ])
    else:
        lines.append("No duplicate method/path candidates detected.")

    lines.extend(["", "## Parsing Errors", ""])

    if report["errors"]:
        for error in report["errors"]:
            lines.append(
                f"- **{escape_markdown(error['file'])}:** "
                f"{escape_markdown(error['error'])}"
            )
    else:
        lines.append("No Python parsing errors detected.")

    lines.extend([
        "",
        "## Limitations",
        "",
        "- This reference scans static HTTP route decorators.",
        "- APIRouter prefixes are not resolved.",
        "- Dynamically registered routes may be absent.",
        "- Authentication and authorization requirements are not inferred.",
        "- Verify endpoint behavior against the running application.",
        "",
    ])

    return "\n".join(lines)


def write_documentation(report, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    content = generate_markdown(report)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")

    temporary.write_text(content, encoding="utf-8")
    temporary.replace(output_path)

    return output_path


def main():
    backend = ROOT / "backend"
    output = ROOT / "docs" / "generated_api_reference.md"

    print("\nINFRA SENTRY AI - API DOCUMENTATION GENERATOR")
    print("=" * 50)

    try:
        report = build_inventory_report(backend)
        write_documentation(report, output)
    except (OSError, ValueError, SyntaxError) as exc:
        print(f"DOCUMENTATION GENERATION FAILED: {exc}")
        return 1

    print(f"Routes documented: {report['summary']['total_routes']}")
    print(f"Documentation: {output}")

    if report["errors"]:
        print("Parsing errors exist. Review the generated document.")
        return 1

    print("\nAPI DOCUMENTATION GENERATED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
