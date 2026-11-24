from pathlib import Path
import argparse
import sys


FINAL_DELIVERABLES = [
    "README.md",
    "docker-compose.yml",
    "backend/Dockerfile",
    "frontend/Dockerfile",
    "frontend/nginx.conf",
    ".github/workflows/ci.yml",
    "scripts/regression_test_runner.py",
    "scripts/release_readiness_check.py",
    "scripts/final_release_audit.py",
    "docs/day111_portfolio_showcase.md",
    "docs/day112_frontend_deployment.md",
    "docs/day118_github_actions_ci.md",
    "docs/day119_release_readiness.md",
]


def inspect_project(root: Path) -> tuple[bool, list[str]]:
    missing = [
        item for item in FINAL_DELIVERABLES
        if not (root / item).is_file()
    ]

    return not missing, missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="InfraSentry AI final project completion check"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    args = parser.parse_args()

    root = args.root.resolve()

    print("\nInfraSentry AI - Final Project Completion")
    print("=" * 55)

    passed, missing = inspect_project(root)

    for item in FINAL_DELIVERABLES:
        status = "PASS" if (root / item).is_file() else "FAIL"
        print(f"[{status}] {item}")

    print("=" * 55)

    if missing:
        print("RESULT: INCOMPLETE")
        print("Missing deliverables:")
        for item in missing:
            print(f" - {item}")
        return 1

    print(f"Deliverables verified: {len(FINAL_DELIVERABLES)}")
    print("RESULT: PROJECT STRUCTURE COMPLETE")
    print("Note: This check does not certify model accuracy or production security.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
