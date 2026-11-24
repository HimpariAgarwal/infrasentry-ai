import tempfile
import unittest
from pathlib import Path

from backend.api_documentation_generator import (
    generate_markdown,
    write_documentation,
)


class TestApiDocumentationGenerator(unittest.TestCase):

    def sample_report(self):
        return {
            "schema_version": "1.0",
            "summary": {
                "passed": True,
                "checked_files": 3,
                "total_routes": 2,
                "files_with_routes": 2,
                "duplicate_candidates": 0,
                "parsing_errors": 0,
            },
            "methods": {"GET": 1, "POST": 1},
            "files": ["router.py", "items.py"],
            "routes": [
                {
                    "method": "GET",
                    "path": "/health",
                    "function": "health",
                    "file": "router.py",
                },
                {
                    "method": "POST",
                    "path": "/items",
                    "function": "create_item",
                    "file": "items.py",
                },
            ],
            "duplicates": [],
            "errors": [],
        }

    def test_generates_document_title(self):
        markdown = generate_markdown(self.sample_report())
        self.assertIn("# InfraSentry AI - API Reference", markdown)

    def test_includes_route_paths(self):
        markdown = generate_markdown(self.sample_report())
        self.assertIn("`/health`", markdown)
        self.assertIn("`/items`", markdown)

    def test_includes_http_methods(self):
        markdown = generate_markdown(self.sample_report())
        self.assertIn("GET", markdown)
        self.assertIn("POST", markdown)

    def test_includes_function_names(self):
        markdown = generate_markdown(self.sample_report())
        self.assertIn("health", markdown)
        self.assertIn("create_item", markdown)

    def test_includes_duplicate_candidates(self):
        report = self.sample_report()
        report["duplicates"] = [
            {"method": "GET", "path": "/health"}
        ]

        markdown = generate_markdown(report)
        self.assertIn("Duplicate Route Candidates", markdown)
        self.assertIn("/health", markdown)

    def test_includes_parsing_errors(self):
        report = self.sample_report()
        report["errors"] = [
            {"file": "broken.py", "error": "Invalid syntax"}
        ]

        markdown = generate_markdown(report)
        self.assertIn("broken.py", markdown)
        self.assertIn("Invalid syntax", markdown)

    def test_writes_documentation_file(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "docs" / "reference.md"

            returned = write_documentation(
                self.sample_report(),
                output,
            )

            self.assertTrue(returned.exists())
            self.assertIn(
                "API Reference",
                returned.read_text(encoding="utf-8"),
            )

    def test_empty_route_inventory(self):
        report = self.sample_report()
        report["routes"] = []
        report["methods"] = {}
        report["summary"]["total_routes"] = 0

        markdown = generate_markdown(report)
        self.assertIn("## Endpoints", markdown)
        self.assertIn("No duplicate", markdown)


if __name__ == "__main__":
    unittest.main()
