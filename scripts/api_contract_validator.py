import argparse
import json
import sys
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


def validate_openapi(document: dict) -> list[str]:
    errors = []

    if not isinstance(document, dict):
        return ["OpenAPI document must be a JSON object"]

    version = document.get("openapi")
    if not isinstance(version, str) or not version.startswith("3."):
        errors.append("Missing or unsupported OpenAPI 3.x version")

    info = document.get("info")
    if not isinstance(info, dict):
        errors.append("Missing info object")
    else:
        if not isinstance(info.get("title"), str) or not info["title"].strip():
            errors.append("Missing API title")
        if not isinstance(info.get("version"), str) or not info["version"].strip():
            errors.append("Missing API version")

    paths = document.get("paths")
    if not isinstance(paths, dict) or not paths:
        errors.append("No API paths found")
        return errors

    valid_methods = {
        "get", "post", "put", "patch", "delete",
        "options", "head", "trace",
    }

    operation_ids = []

    for path, path_item in paths.items():
        if not isinstance(path, str) or not path.startswith("/"):
            errors.append(f"Invalid API path: {path}")
            continue

        if not isinstance(path_item, dict):
            errors.append(f"Invalid path definition: {path}")
            continue

        for method, operation in path_item.items():
            if method.lower() not in valid_methods:
                continue

            if not isinstance(operation, dict):
                errors.append(f"Invalid operation: {method.upper()} {path}")
                continue

            responses = operation.get("responses")
            if not isinstance(responses, dict) or not responses:
                errors.append(f"Missing responses: {method.upper()} {path}")

            operation_id = operation.get("operationId")
            if operation_id is not None:
                if not isinstance(operation_id, str) or not operation_id.strip():
                    errors.append(
                        f"Invalid operationId: {method.upper()} {path}"
                    )
                else:
                    operation_ids.append(operation_id)

    duplicates = sorted({
        item for item in operation_ids
        if operation_ids.count(item) > 1
    })

    for duplicate in duplicates:
        errors.append(f"Duplicate operationId: {duplicate}")

    return errors


def fetch_openapi(url: str, timeout: int = 10) -> dict:
    with urlopen(url, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"OpenAPI endpoint returned {response.status}")

        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="InfraSentry AI OpenAPI contract validator"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000/openapi.json",
        help="OpenAPI JSON endpoint",
    )
    parser.add_argument("--timeout", type=int, default=10)

    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    try:
        document = fetch_openapi(args.url, args.timeout)
        errors = validate_openapi(document)
    except (URLError, HTTPError, OSError, ValueError, RuntimeError) as error:
        print(f"CONTRACT CHECK ERROR: {error}", file=sys.stderr)
        return 2

    print("\nInfraSentry AI - API Contract Report")
    print("=" * 55)

    if errors:
        for error in errors:
            print(f"FAIL: {error}")

        print(f"\nResult: FAILED ({len(errors)} issue(s))")
        return 1

    print(f"OpenAPI version: {document['openapi']}")
    print(f"API title: {document['info']['title']}")
    print(f"API paths inspected: {len(document['paths'])}")
    print("Result: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
