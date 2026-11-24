import ast
from pathlib import Path

IGNORED_DIRS = {
    ".venv",
    "venv",
    "__pycache__",
    "backups",
    "logs",
    "node_modules",
}

HTTP_METHODS = {
    "get", "post", "put", "patch",
    "delete", "options", "head",
}


def extract_routes(source, relative_file):
    tree = ast.parse(source)
    routes = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            function = decorator.func

            if not isinstance(function, ast.Attribute):
                continue

            method = function.attr.lower()

            if method not in HTTP_METHODS:
                continue

            if not decorator.args:
                continue

            path_node = decorator.args[0]

            if not isinstance(path_node, ast.Constant):
                continue

            if not isinstance(path_node.value, str):
                continue

            routes.append({
                "method": method.upper(),
                "path": path_node.value,
                "function": node.name,
                "file": relative_file,
            })

    return routes


def scan_api_routes(source_root):
    source_root = Path(source_root)

    if not source_root.is_dir():
        raise FileNotFoundError(
            f"Backend directory missing: {source_root}"
        )

    routes = []
    errors = []
    checked_files = 0

    for path in sorted(source_root.rglob("*.py")):
        relative = path.relative_to(source_root)

        if any(part in IGNORED_DIRS for part in relative.parts):
            continue

        checked_files += 1

        try:
            source = path.read_text(
                encoding="utf-8-sig",
                errors="strict",
            )
            routes.extend(
                extract_routes(source, relative.as_posix())
            )
        except (SyntaxError, UnicodeDecodeError) as exc:
            errors.append({
                "file": relative.as_posix(),
                "error": str(exc),
            })

    seen = set()
    duplicates = []

    for route in routes:
        key = (route["method"], route["path"])

        if key in seen:
            duplicates.append({
                "method": route["method"],
                "path": route["path"],
            })
        else:
            seen.add(key)

    return {
        "passed": not errors,
        "checked_files": checked_files,
        "route_count": len(routes),
        "routes": routes,
        "duplicates": duplicates,
        "errors": errors,
    }


def main():
    root = Path(__file__).resolve().parent.parent
    backend = root / "backend"

    print("\nINFRA SENTRY AI - API ROUTE INVENTORY")
    print("=" * 48)

    try:
        result = scan_api_routes(backend)
    except (OSError, FileNotFoundError) as exc:
        print(f"INVENTORY ERROR: {exc}")
        return 2

    print(f"Python files scanned: {result['checked_files']}")
    print(f"Routes discovered: {result['route_count']}")

    for route in result["routes"]:
        print(
            f"[{route['method']}] {route['path']} "
            f"| {route['file']} "
            f"| {route['function']}"
        )

    if result["duplicates"]:
        print("\nDuplicate method/path candidates:")
        for item in result["duplicates"]:
            print(f"[REVIEW] {item['method']} {item['path']}")

    if result["errors"]:
        print("\nPython parsing errors:")
        for item in result["errors"]:
            print(f"[ERROR] {item['file']}: {item['error']}")

    if result["passed"]:
        print("\nAPI ROUTE INVENTORY: PASSED")
        print("Review duplicate candidates manually if present.")
        return 0

    print("\nAPI ROUTE INVENTORY: FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
