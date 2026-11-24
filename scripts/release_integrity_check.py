import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
result = subprocess.run(
    [sys.executable, "-m", "unittest", "discover", "-s", "backend", "-p", "test_release_integrity.py", "-v"],
    cwd=ROOT
)
if result.returncode != 0:
    sys.exit(result.returncode)
print("RELEASE INTEGRITY GATE PASSED.")
