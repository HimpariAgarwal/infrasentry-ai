from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REQUIRED_FILES = [
    "README.md",
    "docker-compose.yml",
    "backend/Dockerfile",
    "frontend/Dockerfile",
    "frontend/nginx.conf",
    ".github/workflows/ci.yml",
    "scripts/regression_test_runner.py",
    "scripts/git_security_audit.py",
    "scripts/api_contract_validator.py",
]


def check_required_files(root: Path) -> tuple[bool, str]:
    missing = [
        name for name in REQUIRED_FILES
        if not (root / name).is_file()
    ]

    if missing:
        return False, "Missing files: " + ", ".join(missing)

    return True, f"All {len(REQUIRED_FILES)} required files exist."


def is_sensitive_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    parts = normalized.split("/")
    filename = parts[-1]

    if any(part in {"backups", ".venv", "node_modules"} for part in parts):
        return True

    if filename in {
        ".env",
        "id_rsa",
        "id_ed25519",
        "credentials.json",
        "secrets.json",
    }:
        return True

    if filename.endswith((".pem", ".p12", ".pfx")):
        return True

    return False


def check_tracked_sensitive_files(root: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return False, "Unable to inspect tracked Git files."

    tracked = [item for item in result.stdout.split("\0") if item]
    sensitive = [item for item in tracked if is_sensitive_path(item)]

    if sensitive:
        return False, "Sensitive tracked paths: " + ", ".join(sensitive)

    return True, f"Checked {len(tracked)} tracked paths; no sensitive paths found."


def check_docker_compose(root: Path) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["docker", "compose", "config", "-q"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False, "Docker CLI is not available."

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        return False, detail or "Docker Compose validation failed."

    return True, "Docker Compose configuration is valid."


def run_readiness(
    root: Path,
    skip_docker: bool = False,
) -> tuple[bool, list[tuple[str, bool, str]]]:
    checks = []

    checks.append(("Required project files", *check_required_files(root)))
    checks.append(("Git security", *check_tracked_sensitive_files(root)))

    if not skip_docker:
        checks.append(("Docker Compose", *check_docker_compose(root)))

    passed = all(item[1] for item in checks)
    return passed, checks


def main() -> int:
    parser = argparse.ArgumentParser(
        description="InfraSentry AI production release readiness gate"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    parser.add_argument(
        "--skip-docker",
        action="store_true",
        help="Skip Docker Compose validation.",
    )
    args = parser.parse_args()

    root = args.root.resolve()

    print("\nInfraSentry AI - Release Readiness Gate")
    print("=" * 52)

    passed, checks = run_readiness(root, args.skip_docker)

    for name, success, detail in checks:
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {name}: {detail}")

    print("=" * 52)
    print("RESULT:", "READY" if passed else "NOT READY")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
