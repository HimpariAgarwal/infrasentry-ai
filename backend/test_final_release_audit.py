import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.final_release_audit import (
    audit_gitignore,
    audit_python_syntax,
    audit_required_files,
    audit_sensitive_files,
    is_sensitive_path,
    run_final_audit,
    write_audit_report,
)


class TestFinalReleaseAudit(unittest.TestCase):

    def create_project(self, root):
        files = [
            "backend/main.py",
            "frontend/package.json",
            "frontend/src/App.tsx",
            "docs/day100_final_release_audit.md",
        ]

        for relative in files:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("sample = True", encoding="utf-8")

        (root / ".gitignore").write_text(
            ".env\n__pycache__\nnode_modules\nlogs\nbackups\n",
            encoding="utf-8",
        )

    def test_required_files_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_project(root)

            result = audit_required_files(root)
            self.assertTrue(result["passed"])

    def test_missing_required_files_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            result = audit_required_files(Path(temp))
            self.assertFalse(result["passed"])

    def test_python_syntax_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "backend").mkdir()
            (root / "backend" / "valid.py").write_text(
                "value = 10",
                encoding="utf-8",
            )

            result = audit_python_syntax(root)
            self.assertTrue(result["passed"])
            self.assertEqual(result["checked_files"], 1)

    def test_python_syntax_error_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "backend").mkdir()
            (root / "backend" / "broken.py").write_text(
                "def invalid(:",
                encoding="utf-8",
            )

            result = audit_python_syntax(root)
            self.assertFalse(result["passed"])
            self.assertEqual(len(result["errors"]), 1)

    def test_env_is_sensitive(self):
        self.assertTrue(is_sensitive_path("backend/.env"))

    def test_env_template_is_allowed(self):
        self.assertFalse(
            is_sensitive_path("backend/.env.example")
        )

    def test_model_weight_is_sensitive(self):
        self.assertTrue(
            is_sensitive_path("backend/model.pt")
        )

    def test_sensitive_tracked_file_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            with patch(
                "backend.final_release_audit.get_tracked_files",
                return_value=[
                    "backend/main.py",
                    "backend/.env",
                ],
            ):
                result = audit_sensitive_files(root)

            self.assertFalse(result["passed"])
            self.assertIn(
                "backend/.env",
                result["sensitive_files"],
            )

    def test_gitignore_patterns_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_project(root)

            result = audit_gitignore(root)
            self.assertTrue(result["passed"])

    def test_gitignore_missing_pattern_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".gitignore").write_text(
                ".env\n",
                encoding="utf-8",
            )

            result = audit_gitignore(root)
            self.assertFalse(result["passed"])

    def test_final_audit_report_structure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_project(root)

            with patch(
                "backend.final_release_audit.get_tracked_files",
                return_value=[
                    "backend/main.py",
                    "frontend/package.json",
                ],
            ):
                report = run_final_audit(root)

            self.assertEqual(report["summary"]["total_checks"], 4)
            self.assertTrue(report["summary"]["passed"])

    def test_report_is_written(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "audit.json"

            report = {
                "schema_version": "1.0",
                "summary": {"passed": True},
            }

            returned = write_audit_report(report, output)

            self.assertTrue(returned.exists())
            self.assertIn(
                '"passed": true',
                returned.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
