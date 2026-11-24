import tempfile
import unittest
from pathlib import Path

from backend.python_integrity_audit import (
    audit_python_files,
    discover_python_files,
)


class TestPythonIntegrityAudit(unittest.TestCase):

    def create_file(self, root, relative, content):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_valid_python_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(root, "main.py", "value = 10\n")

            result = audit_python_files(root)
            self.assertTrue(result["passed"])
            self.assertEqual(result["checked_files"], 1)

    def test_invalid_python_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(root, "broken.py", "def broken(\n")

            result = audit_python_files(root)
            self.assertFalse(result["passed"])
            self.assertEqual(len(result["errors"]), 1)

    def test_multiple_files_are_scanned(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(root, "main.py", "x = 1\n")
            self.create_file(root, "service.py", "y = 2\n")

            result = audit_python_files(root)
            self.assertEqual(result["checked_files"], 2)
            self.assertTrue(result["passed"])

    def test_virtual_environment_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(root, "main.py", "x = 1\n")
            self.create_file(root, ".venv/lib/broken.py", "def broken(\n")

            files = discover_python_files(root)
            self.assertEqual(len(files), 1)

    def test_backups_are_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(root, "main.py", "x = 1\n")
            self.create_file(root, "backups/old.py", "def broken(\n")

            result = audit_python_files(root)
            self.assertTrue(result["passed"])
            self.assertEqual(result["checked_files"], 1)

    def test_cache_directories_are_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(root, "main.py", "x = 1\n")
            self.create_file(
                root,
                "__pycache__/cached.py",
                "def broken(\n",
            )

            result = audit_python_files(root)
            self.assertEqual(result["checked_files"], 1)
            self.assertTrue(result["passed"])

    def test_nested_python_files_are_scanned(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(
                root,
                "services/nested/service.py",
                "def valid():\n    return True\n",
            )

            result = audit_python_files(root)
            self.assertEqual(result["checked_files"], 1)
            self.assertTrue(result["passed"])

    def test_missing_backend_directory_raises_error(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing"

            with self.assertRaises(FileNotFoundError):
                audit_python_files(missing)


if __name__ == "__main__":
    unittest.main()
