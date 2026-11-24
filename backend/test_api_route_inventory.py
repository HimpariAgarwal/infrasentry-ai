import tempfile
import unittest
from pathlib import Path

from backend.api_route_inventory import (
    extract_routes,
    scan_api_routes,
)


class TestApiRouteInventory(unittest.TestCase):

    def create_file(self, root, relative, content):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_extracts_get_route(self):
        routes = extract_routes(
            '@router.get("/health")\ndef health():\n    pass\n',
            "router.py",
        )
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["method"], "GET")
        self.assertEqual(routes[0]["path"], "/health")

    def test_extracts_post_route(self):
        routes = extract_routes(
            '@router.post("/items")\ndef create_item():\n    pass\n',
            "router.py",
        )
        self.assertEqual(routes[0]["method"], "POST")

    def test_extracts_async_route(self):
        routes = extract_routes(
            '@router.get("/async")\nasync def async_route():\n    pass\n',
            "router.py",
        )
        self.assertEqual(routes[0]["function"], "async_route")

    def test_ignores_non_http_decorators(self):
        routes = extract_routes(
            '@router.on_event("startup")\ndef startup():\n    pass\n',
            "router.py",
        )
        self.assertEqual(routes, [])

    def test_detects_duplicate_candidates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(
                root,
                "router.py",
                '@router.get("/health")\ndef first(): pass\n'
                '@app.get("/health")\ndef second(): pass\n',
            )

            result = scan_api_routes(root)
            self.assertEqual(len(result["duplicates"]), 1)

    def test_scans_multiple_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(
                root,
                "first.py",
                '@router.get("/one")\ndef one(): pass\n',
            )
            self.create_file(
                root,
                "nested/second.py",
                '@router.post("/two")\ndef two(): pass\n',
            )

            result = scan_api_routes(root)
            self.assertEqual(result["checked_files"], 2)
            self.assertEqual(result["route_count"], 2)

    def test_ignores_virtual_environment(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(
                root,
                "router.py",
                '@router.get("/health")\ndef health(): pass\n',
            )
            self.create_file(
                root,
                ".venv/lib/package.py",
                '@router.get("/ignored")\ndef ignored(): pass\n',
            )

            result = scan_api_routes(root)
            self.assertEqual(result["checked_files"], 1)
            self.assertEqual(result["route_count"], 1)

    def test_reports_invalid_python(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(root, "broken.py", "def broken(\n")

            result = scan_api_routes(root)
            self.assertFalse(result["passed"])
            self.assertEqual(len(result["errors"]), 1)


if __name__ == "__main__":
    unittest.main()
