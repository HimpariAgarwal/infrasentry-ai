import tempfile
import unittest
from pathlib import Path

from backend.api_documentation_validator import (
    validate_documentation,
    write_validation_report,
)


class TestApiDocumentationValidator(unittest.TestCase):

    def sample_report(self):
        return {
            "summary": {
                "total_routes": 2,
                "parsing_errors": 0,
            },
            "methods": {
                "GET": 1,
                "POST": 1,
            },
            "routes": [
                {"method": "GET", "path": "/health"},
                {"method": "POST", "path": "/items"},
            ],
        }

    def sample_markdown(self):
        return """
| Method | Route Count |
|---|---:|
| GET | 1 |
| POST | 1 |

| Method | Endpoint | Function | Source File |
|---|---|---|---|
| GET | `/health` | `health` | `router.py` |
| POST | `/items` | `create_item` | `items.py` |
"""

    def test_valid_documentation_passes(self):
        result = validate_documentation(
            self.sample_report(),
            self.sample_markdown(),
        )
        self.assertTrue(result["passed"])

    def test_missing_route_fails(self):
        markdown = self.sample_markdown().replace(
            "| POST | `/items` | `create_item` | `items.py` |",
            "",
        )
        result = validate_documentation(
            self.sample_report(),
            markdown,
        )
        self.assertFalse(result["passed"])
        self.assertEqual(result["missing_route_count"], 1)

    def test_missing_method_distribution_fails(self):
        markdown = self.sample_markdown().replace(
            "| POST | 1 |",
            "",
        )
        result = validate_documentation(
            self.sample_report(),
            markdown,
        )
        self.assertFalse(result["passed"])
        self.assertIn("POST", result["missing_methods"])

    def test_parsing_errors_fail_validation(self):
        report = self.sample_report()
        report["summary"]["parsing_errors"] = 1

        result = validate_documentation(
            report,
            self.sample_markdown(),
        )
        self.assertFalse(result["passed"])

    def test_empty_inventory_passes(self):
        report = {
            "summary": {"total_routes": 0, "parsing_errors": 0},
            "methods": {},
            "routes": [],
        }

        result = validate_documentation(report, "")
        self.assertTrue(result["passed"])

    def test_reports_all_missing_routes(self):
        result = validate_documentation(
            self.sample_report(),
            "",
        )
        self.assertEqual(result["missing_route_count"], 2)

    def test_validation_report_is_written(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "validation.json"
            result = validate_documentation(
                self.sample_report(),
                self.sample_markdown(),
            )

            returned = write_validation_report(result, output)

            self.assertTrue(returned.exists())
            self.assertIn(
                '"passed": true',
                returned.read_text(encoding="utf-8"),
            )

    def test_report_contains_schema_version(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "validation.json"
            result = validate_documentation(
                self.sample_report(),
                self.sample_markdown(),
            )
            write_validation_report(result, output)

            import json
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], "1.0")


if __name__ == "__main__":
    unittest.main()
