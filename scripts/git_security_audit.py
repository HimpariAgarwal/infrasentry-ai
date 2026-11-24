import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AuditResult:
    passed: bool
    findings: list[str]


SENSITIVE_NAMES = {
    ".env",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "secrets.json",
    "service-account.json",
}

SENSITIVE_EXTENSIONS = {
    ".pem",
    ".p12",
    ".pfx",
    ".key",
}

FORBIDDEN_DIRECTORIES = {
    "backups",
    "__pycache__",
    "node_modules",
    ".venv",
}


def is_sensitive_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    parts = normalized.split("/")
    filename = parts[-1]

    if filename in SENSITIVE_NAMES:
        return True

    if filename.startswith(".env.") and filename not in {
        ".env.example",
        ".env.template",
    }:
        return True

    if Path(filename).suffix.lower() in SENSITIVE_EXTENSIONS:
        return True

    if any(part in FORBIDDEN_DIRECTORIES for part in parts[:-1]):
        return True

    return False


def audit_tracked_files(paths: list[str]) -> AuditResult:
    findings = [
        path for path in paths
        if is_sensitive_path(path)
    ]

    return AuditResult(
        passed=len(findings) == 0,
        findings=findings,
    )


def get_tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or "Unable to inspect Git files"
        )

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="InfraSentry AI Git security audit"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Git repository root",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()

    try:
        tracked = get_tracked_files(root)
        result = audit_tracked_files(tracked)
    except (RuntimeError, OSError) as error:
        print(f"AUDIT ERROR: {error}", file=sys.stderr)
        return 2

    print("\nInfraSentry AI - Git Security Audit")
    print("=" * 55)
    print(f"Tracked files inspected: {len(tracked)}")

    if result.findings:
        print("\nSECURITY FINDINGS:")
        for finding in result.findings:
            print(f"  - {finding}")
        print("\nRESULT: FAILED")
        return 1

    print("\nNo known sensitive filenames detected.")
    print("RESULT: PASSED")
    print("=" * 55)
    return 0


if __name__ == "__main__":
    sys.exit(main())
