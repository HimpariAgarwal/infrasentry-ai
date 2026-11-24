from pathlib import Path
import subprocess


REQUIRED_FILES = [
    "backend/main.py",
    "frontend/package.json",
    "frontend/src/App.tsx",
]

SAFE_ENV_TEMPLATES = {
    ".env.example",
    ".env.sample",
    ".env.template",
}

WEIGHT_EXTENSIONS = {".pt", ".pth", ".weights", ".onnx"}


def is_sensitive_tracked_file(file_path):
    normalized = file_path.replace("\\", "/").lower()
    parts = normalized.split("/")
    name = parts[-1]

    if name == ".env" or (
        name.startswith(".env.")
        and name not in SAFE_ENV_TEMPLATES
    ):
        return True

    if any(part in {"node_modules", "datasets", "dataset", "logs"} for part in parts):
        return True

    if Path(name).suffix.lower() in WEIGHT_EXTENSIONS:
        return True

    return False


def run_release_audit(root, tracked_files=None):
    root = Path(root)

    missing_files = [
        relative for relative in REQUIRED_FILES
        if not (root / relative).is_file()
    ]

    if tracked_files is None:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        tracked_files = result.stdout.splitlines()

    sensitive_files = [
        item for item in tracked_files
        if is_sensitive_tracked_file(item)
    ]

    return {
        "passed": not missing_files and not sensitive_files,
        "missing_files": missing_files,
        "sensitive_tracked_files": sensitive_files,
        "tracked_file_count": len(tracked_files),
    }


def main():
    root = Path(__file__).resolve().parent.parent

    print("\nINFRA SENTRY AI - RELEASE READINESS AUDIT")
    print("=" * 48)

    try:
        result = run_release_audit(root)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"Git audit could not run: {exc}")
        return 2

    print(f"Tracked files checked: {result['tracked_file_count']}")

    print("\nRequired files:")
    if result["missing_files"]:
        for item in result["missing_files"]:
            print(f"[MISSING] {item}")
    else:
        print("[PASS] All required files exist.")

    print("\nSensitive tracked files:")
    if result["sensitive_tracked_files"]:
        for item in result["sensitive_tracked_files"]:
            print(f"[WARNING] {item}")
    else:
        print("[PASS] No sensitive tracked paths detected.")

    if result["passed"]:
        print("\nRELEASE READINESS AUDIT: PASSED")
        return 0

    print("\nRELEASE READINESS AUDIT: FAILED")
    print("Resolve the listed issues before release.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
