import tempfile
import unittest
from pathlib import Path

from backend.release_readiness_audit import (
    is_sensitive_tracked_file,
    run_release_audit,
)


class TestReleaseReadinessAudit(unittest.TestCase):

    def create_project(self, root):
        for relative in (
            "backend/main.py",
            "frontend/package.json",
            "frontend/src/App.tsx",
        ):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("test", encoding="utf-8")

    def test_passes_with_required_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_project(root)

            result = run_release_audit(root, [])
            self.assertTrue(result["passed"])

    def test_detects_missing_required_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_project(root)
            (root / "frontend/package.json").unlink()

            result = run_release_audit(root, [])
            self.assertFalse(result["passed"])
            self.assertIn("frontend/package.json", result["missing_files"])

    def test_detects_env_file(self):
        self.assertTrue(is_sensitive_tracked_file("backend/.env"))

    def test_allows_env_example(self):
        self.assertFalse(is_sensitive_tracked_file("backend/.env.example"))

    def test_detects_model_weights(self):
        self.assertTrue(is_sensitive_tracked_file("backend/weights/model.pt"))

    def test_detects_datasets(self):
        self.assertTrue(is_sensitive_tracked_file("datasets/train/image.jpg"))

    def test_detects_runtime_logs(self):
        self.assertTrue(
            is_sensitive_tracked_file("backend/logs/metrics.json")
        )

    def test_detects_node_modules(self):
        self.assertTrue(
            is_sensitive_tracked_file("frontend/node_modules/package/file.js")
        )

    def test_clean_tracked_files_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_project(root)

            tracked = [
                "backend/main.py",
                "frontend/package.json",
                "frontend/src/App.tsx",
                "README.md",
                "backend/.env.example",
            ]

            result = run_release_audit(root, tracked)
            self.assertTrue(result["passed"])
            self.assertEqual(result["sensitive_tracked_files"], [])

    def test_sensitive_tracked_file_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_project(root)

            result = run_release_audit(root, ["backend/.env"])
            self.assertFalse(result["passed"])
            self.assertIn(
                "backend/.env",
                result["sensitive_tracked_files"],
            )


if __name__ == "__main__":
    unittest.main()
