import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "backend/main.py",
    "frontend/package.json",
    "frontend/src/App.tsx",
    "docs/day100_final_release_audit.md",
]

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "backups",
    "logs",
    "datasets",
    "dataset",
    "weights",
    "runs",
    ".pytest_cache",
}

SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
}

SENSITIVE_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".pt",
    ".pth",
    ".onnx",
    ".engine",
}


def get_tracked_files(root):
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )

    return sorted(
        line.strip().replace("\\", "/")
        for line in result.stdout.splitlines()
        if line.strip()
    )


def is_sensitive_path(relative_path):
    path = Path(relative_path)
    name = path.name.lower()

    if name in {".env.example", ".env.template"}:
        return False

    if name in SENSITIVE_NAMES:
        return True

    if path.suffix.lower() in SENSITIVE_SUFFIXES:
        return True

    if any(part.lower() in EXCLUDED_DIRS for part in path.parts):
        return True

    return False


def audit_required_files(root):
    missing = [
        relative
        for relative in REQUIRED_FILES
        if not (root / relative).is_file()
    ]

    return {
        "passed": not missing,
        "missing": missing,
    }


def audit_python_syntax(root):
    errors = []
    checked = 0

    backend = root / "backend"

    if not backend.exists():
        return {
            "passed": False,
            "checked_files": 0,
            "errors": ["backend directory missing"],
        }

    for path in backend.rglob("*.py"):
        relative = path.relative_to(root)

        if any(
            part.lower() in EXCLUDED_DIRS
            for part in relative.parts
        ):
            continue

        try:
            source = path.read_text(
                encoding="utf-8-sig"
            )
            ast.parse(source, filename=str(relative))
            checked += 1

        except (SyntaxError, UnicodeError, OSError) as exc:
            errors.append({
                "file": relative.as_posix(),
                "error": str(exc),
            })

    return {
        "passed": not errors,
        "checked_files": checked,
        "errors": errors,
    }


def audit_sensitive_files(root):
    try:
        tracked = get_tracked_files(root)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return {
            "passed": False,
            "sensitive_files": [],
            "error": str(exc),
        }

    sensitive = [
        path
        for path in tracked
        if is_sensitive_path(path)
    ]

    return {
        "passed": not sensitive,
        "sensitive_files": sensitive,
    }


def audit_gitignore(root):
    path = root / ".gitignore"

    if not path.is_file():
        return {
            "passed": False,
            "missing_patterns": [".gitignore file"],
        }

    content = path.read_text(
        encoding="utf-8-sig"
    )

    required_patterns = [
        ".env",
        "__pycache__",
        "node_modules",
        "logs",
        "backups",
    ]

    missing = [
        pattern
        for pattern in required_patterns
        if pattern not in content
    ]

    return {
        "passed": not missing,
        "missing_patterns": missing,
    }


def run_final_audit(root=ROOT):
    root = Path(root)

    checks = {
        "required_files": audit_required_files(root),
        "python_syntax": audit_python_syntax(root),
        "sensitive_files": audit_sensitive_files(root),
        "gitignore": audit_gitignore(root),
    }

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "InfraSentry AI",
        "checks": checks,
        "summary": {
            "total_checks": len(checks),
            "passed_checks": sum(
                1 for item in checks.values()
                if item["passed"]
            ),
            "failed_checks": sum(
                1 for item in checks.values()
                if not item["passed"]
            ),
            "passed": all(
                item["passed"]
                for item in checks.values()
            ),
        },
    }


def write_audit_report(report, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    temporary = output_path.with_suffix(
        output_path.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    temporary.replace(output_path)
    return output_path


def main():
    output = (
        ROOT / "backend" / "logs"
        / "day100_final_release_audit.json"
    )

    try:
        report = run_final_audit(ROOT)
        write_audit_report(report, output)

    except (OSError, ValueError) as exc:
        print(f"FINAL AUDIT ERROR: {exc}")
        return 1

    print("\nINFRA SENTRY AI - FINAL RELEASE AUDIT")
    print("=" * 52)

    for name, result in report["checks"].items():
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{name}: {status}")

        for key in (
            "missing",
            "missing_patterns",
            "sensitive_files",
            "errors",
        ):
            value = result.get(key)

            if value:
                print(f"  {key}: {value}")

    summary = report["summary"]

    print("-" * 52)
    print(f"Checks passed: {summary['passed_checks']}")
    print(f"Checks failed: {summary['failed_checks']}")
    print(f"FINAL STATUS: {'PASS' if summary['passed'] else 'FAIL'}")
    print(f"Report: {output}")

    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
