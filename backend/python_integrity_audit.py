import ast
from pathlib import Path

IGNORED_DIRS = {
    ".venv",
    "venv",
    "__pycache__",
    "backups",
    "logs",
    "node_modules",
    ".pytest_cache",
}


def discover_python_files(source_root):
    source_root = Path(source_root)

    if not source_root.is_dir():
        raise FileNotFoundError(
            f"Backend directory not found: {source_root}"
        )

    files = []

    for path in source_root.rglob("*.py"):
        relative_parts = path.relative_to(source_root).parts

        if any(part in IGNORED_DIRS for part in relative_parts):
            continue

        files.append(path)

    return sorted(files)


def audit_python_files(source_root):
    source_root = Path(source_root)
    files = discover_python_files(source_root)

    errors = []

    for path in files:
        try:
            content = path.read_text(
                encoding="utf-8-sig",
                errors="strict",
            )
            ast.parse(content, filename=str(path))

        except (SyntaxError, UnicodeDecodeError) as exc:
            errors.append({
                "file": str(path.relative_to(source_root)),
                "error": str(exc),
                "line": getattr(exc, "lineno", None),
            })

    return {
        "passed": len(errors) == 0,
        "checked_files": len(files),
        "errors": errors,
    }


def main():
    root = Path(__file__).resolve().parent.parent
    backend = root / "backend"

    print("\nINFRA SENTRY AI - BACKEND PYTHON AUDIT")
    print("=" * 48)

    try:
        result = audit_python_files(backend)
    except (OSError, FileNotFoundError) as exc:
        print(f"AUDIT ERROR: {exc}")
        return 2

    print(f"Python files checked: {result['checked_files']}")

    if result["errors"]:
        print("\nSyntax errors detected:")

        for item in result["errors"]:
            print(f"\n[ERROR] {item['file']}")
            print(item["error"])

        print("\nBACKEND PYTHON AUDIT: FAILED")
        return 1

    print("\n[PASS] No Python syntax errors detected.")
    print("BACKEND PYTHON AUDIT: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
