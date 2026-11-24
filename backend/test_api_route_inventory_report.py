import json
import tempfile
import unittest
from pathlib import Path

from backend.api_route_inventory_report import (
    build_inventory_report,
    write_inventory_report,
)


class TestApiInventoryReport(unittest.TestCase):

    def create_file(self, root, relative, content):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def prepare_project(self, root):
        self.create_file(
            root,
            "router.py",
            '@router.get("/health")\ndef health(): pass\n'
            '@router.post("/items")\ndef create_item(): pass\n',
        )

    def test_report_schema_version(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.prepare_project(root)

            report = build_inventory_report(root)
            self.assertEqual(report["schema_version"], "1.0")

    def test_total_route_count(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.prepare_project(root)

            report = build_inventory_report(root)
            self.assertEqual(report["summary"]["total_routes"], 2)

    def test_http_method_distribution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.prepare_project(root)

            report = build_inventory_report(root)
            self.assertEqual(report["methods"], {
                "GET": 1,
                "POST": 1,
            })

    def test_route_files_are_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.prepare_project(root)

            report = build_inventory_report(root)
            self.assertIn("router.py", report["files"])

    def test_duplicate_candidates_are_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(
                root,
                "router.py",
                '@router.get("/health")\ndef first(): pass\n'
                '@app.get("/health")\ndef second(): pass\n',
            )

            report = build_inventory_report(root)
            self.assertEqual(
                report["summary"]["duplicate_candidates"], 1
            )

    def test_json_report_is_written(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.prepare_project(root)
            output = root / "reports" / "inventory.json"

            write_inventory_report(root, output)

            self.assertTrue(output.exists())
            loaded = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(loaded["summary"]["total_routes"], 2)

    def test_invalid_python_error_is_in_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(root, "broken.py", "def broken(\n")

            report = build_inventory_report(root)
            self.assertFalse(report["summary"]["passed"])
            self.assertEqual(report["summary"]["parsing_errors"], 1)

    def test_empty_project_produces_valid_report(self):
        with tempfile.TemporaryDirectory() as temp:
            report = build_inventory_report(Path(temp))

            self.assertEqual(report["summary"]["total_routes"], 0)
            self.assertEqual(report["methods"], {})


if __name__ == "__main__":
    unittest.main()
