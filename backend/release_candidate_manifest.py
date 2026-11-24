import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "backend/main.py",
    "frontend/package.json",
    "frontend/src/App.tsx",
    "docs/day99_release_candidate_manifest.md",
]

EXCLUDED_PARTS = {
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

EXCLUDED_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
}

EXCLUDED_SUFFIXES = {
    ".pt",
    ".pth",
    ".onnx",
    ".engine",
    ".pyc",
    ".pyo",
}


def is_excluded(relative_path):
    path = Path(relative_path)

    if any(part.lower() in EXCLUDED_PARTS for part in path.parts):
        return True

    if path.name.lower() in EXCLUDED_NAMES:
        return True

    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return True

    return False


def sha256_file(path):
    digest = hashlib.sha256()

    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def get_git_metadata(root):
    def git_value(*args):
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    try:
        return {
            "commit": git_value("rev-parse", "HEAD"),
            "branch": git_value("branch", "--show-current"),
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            "commit": None,
            "branch": None,
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


def build_manifest(root=ROOT):
    root = Path(root)

    missing_required = [
        relative
        for relative in REQUIRED_FILES
        if not (root / relative).is_file()
    ]

    files = []

    for relative in get_tracked_files(root):
        if is_excluded(relative):
            continue

        path = root / relative

        if not path.is_file():
            continue

        files.append({
            "path": relative,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })

    files.sort(key=lambda item: item["path"])

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "InfraSentry AI",
        "git": get_git_metadata(root),
        "summary": {
            "tracked_files_hashed": len(files),
            "missing_required_files": len(missing_required),
            "passed": not missing_required,
        },
        "missing_required_files": missing_required,
        "files": files,
    }


def write_manifest(manifest, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    temporary = output_path.with_suffix(
        output_path.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    temporary.replace(output_path)
    return output_path


def main():
    output = ROOT / "backend" / "logs" / "release_candidate_manifest.json"

    try:
        manifest = build_manifest(ROOT)
        write_manifest(manifest, output)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Manifest generation failed: {exc}")
        return 1

    summary = manifest["summary"]

    print("\nINFRA SENTRY AI - RELEASE MANIFEST")
    print("=" * 48)
    print(f"Git commit: {manifest['git']['commit']}")
    print(f"Git branch: {manifest['git']['branch']}")
    print(f"Files hashed: {summary['tracked_files_hashed']}")
    print(f"Missing required files: {summary['missing_required_files']}")
    print(f"Status: {'PASS' if summary['passed'] else 'FAIL'}")
    print(f"Manifest: {output}")

    for item in manifest["missing_required_files"]:
        print(f"MISSING: {item}")

    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
