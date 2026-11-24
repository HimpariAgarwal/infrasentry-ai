from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

required_files = [
    "backend/main.py",
    "backend/Dockerfile",
    "backend/requirements.txt",
    "docker-compose.yml",
    ".dockerignore",
    ".gitignore",
    "scripts/e2e_smoke.py",
    "docs/day109_docker_deployment.md",
    "data/processed/yolo_runs/baseline_v1/weights/best.pt",
]

failed = False

print("\n===== INFRASENTRY AI RELEASE AUDIT =====")

for item in required_files:
    exists = (ROOT / item).is_file()
    print(f"[{'PASS' if exists else 'FAIL'}] Required file: {item}")
    if not exists:
        failed = True

requirements = (ROOT / "backend/requirements.txt").read_text(
    encoding="utf-8-sig"
).lower()

for dependency in ("apscheduler==", "pyjwt=="):
    found = dependency in requirements
    print(f"[{'PASS' if found else 'FAIL'}] Dependency: {dependency}")
    if not found:
        failed = True

dockerignore = (ROOT / ".dockerignore").read_text(
    encoding="utf-8-sig"
)
for rule in ("**/.env", "backups"):
    found = rule in dockerignore
    print(f"[{'PASS' if found else 'FAIL'}] Docker ignore rule: {rule}")
    if not found:
        failed = True

result = subprocess.run(
    ["git", "ls-files"],
    cwd=ROOT,
    capture_output=True,
    text=True,
)
if result.returncode != 0:
    print("[FAIL] Could not inspect Git tracked files.")
    failed = True
else:
    tracked_env = [
        item for item in result.stdout.splitlines()
        if Path(item).name.lower() == ".env"
    ]
    if tracked_env:
        print("[FAIL] Environment files are still tracked:")
        for item in tracked_env:
            print(f"       {item}")
        failed = True
    else:
        print("[PASS] No .env files tracked by Git")

if failed:
    print("\nRELEASE AUDIT FAILED.")
    sys.exit(1)

print("\nRELEASE AUDIT PASSED.")
