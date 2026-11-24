import re
from pathlib import Path

SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}

RESOLVE_EXTENSIONS = [
    ".ts", ".tsx", ".js", ".jsx",
    ".css", ".json", ".svg",
    ".png", ".jpg", ".jpeg", ".webp",
]

IMPORT_PATTERN = re.compile(
    r"""(?:\bfrom\s*|\bimport\s*)["'](\.[^"']+)["']"""
)


def resolve_local_import(source_file, import_path):
    target = (source_file.parent / import_path).resolve()

    if target.is_file():
        return target

    for extension in RESOLVE_EXTENSIONS:
        candidate = Path(str(target) + extension)
        if candidate.is_file():
            return candidate

    for extension in RESOLVE_EXTENSIONS:
        candidate = target / ("index" + extension)
        if candidate.is_file():
            return candidate

    return None


def audit_imports(source_root):
    source_root = Path(source_root).resolve()
    unresolved = []
    checked = 0

    if not source_root.is_dir():
        raise FileNotFoundError(
            f"Frontend source directory missing: {source_root}"
        )

    for source_file in source_root.rglob("*"):
        if not source_file.is_file():
            continue

        if source_file.suffix.lower() not in SOURCE_EXTENSIONS:
            continue

        checked += 1
        content = source_file.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

        for match in IMPORT_PATTERN.finditer(content):
            import_path = match.group(1)

            if resolve_local_import(source_file, import_path) is None:
                unresolved.append({
                    "file": str(source_file.relative_to(source_root)),
                    "import": import_path,
                })

    return {
        "passed": len(unresolved) == 0,
        "checked_files": checked,
        "unresolved_imports": unresolved,
    }


def main():
    project_root = Path(__file__).resolve().parent.parent
    source_root = project_root / "frontend" / "src"

    print("\nINFRA SENTRY AI - FRONTEND IMPORT AUDIT")
    print("=" * 48)

    try:
        result = audit_imports(source_root)
    except (OSError, FileNotFoundError) as exc:
        print(f"AUDIT ERROR: {exc}")
        return 2

    print(f"Source files checked: {result['checked_files']}")

    if result["unresolved_imports"]:
        print("\nUnresolved local imports:")
        for item in result["unresolved_imports"]:
            print(f"[MISSING] {item['file']} -> {item['import']}")

        print("\nIMPORT AUDIT: FAILED")
        return 1

    print("\n[PASS] All relative imports resolved.")
    print("IMPORT AUDIT: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
