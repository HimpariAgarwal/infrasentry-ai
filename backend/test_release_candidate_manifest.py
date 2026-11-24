import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.release_candidate_manifest import (
    build_manifest,
    is_excluded,
    sha256_file,
    write_manifest,
)


class TestReleaseCandidateManifest(unittest.TestCase):

    def create_project(self, root):
        files = [
            "backend/main.py",
            "frontend/package.json",
            "frontend/src/App.tsx",
            "docs/day99_release_candidate_manifest.md",
            "backend/example.py",
            "backend/.env",
            "backend/logs/runtime.json",
            "datasets/sample.csv",
            "backend/model.pt",
            "backups/old.py",
            "frontend/node_modules/example.js",
        ]

        for relative in files:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("sample content", encoding="utf-8")

    def test_sha256_matches_expected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.txt"
            path.write_text("hello", encoding="utf-8")

            expected = hashlib.sha256(b"hello").hexdigest()
            self.assertEqual(sha256_file(path), expected)

    def test_env_is_excluded(self):
        self.assertTrue(is_excluded("backend/.env"))

    def test_logs_are_excluded(self):
        self.assertTrue(is_excluded("backend/logs/runtime.json"))

    def test_datasets_are_excluded(self):
        self.assertTrue(is_excluded("datasets/sample.csv"))

    def test_model_weights_are_excluded(self):
        self.assertTrue(is_excluded("backend/model.pt"))

    def test_backups_are_excluded(self):
        self.assertTrue(is_excluded("backups/old.py"))

    def test_node_modules_are_excluded(self):
        self.assertTrue(is_excluded("frontend/node_modules/example.js"))

    def test_manifest_hashes_allowed_files_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_project(root)

            with patch(
                "backend.release_candidate_manifest.get_tracked_files",
                return_value=[
                    "backend/main.py",
                    "frontend/package.json",
                    "frontend/src/App.tsx",
                    "docs/day99_release_candidate_manifest.md",
                    "backend/example.py",
                    "backend/.env",
                    "backend/logs/runtime.json",
                    "datasets/sample.csv",
                    "backend/model.pt",
                    "backups/old.py",
                    "frontend/node_modules/example.js",
                ],
            ), patch(
                "backend.release_candidate_manifest.get_git_metadata",
                return_value={"commit": "abc123", "branch": "main"},
            ):
                manifest = build_manifest(root)

            paths = [item["path"] for item in manifest["files"]]

            self.assertIn("backend/example.py", paths)
            self.assertNotIn("backend/.env", paths)
            self.assertNotIn("backend/logs/runtime.json", paths)
            self.assertNotIn("datasets/sample.csv", paths)
            self.assertNotIn("backend/model.pt", paths)
            self.assertNotIn("backups/old.py", paths)
            self.assertNotIn("frontend/node_modules/example.js", paths)

    def test_missing_required_files_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            with patch(
                "backend.release_candidate_manifest.get_tracked_files",
                return_value=[],
            ), patch(
                "backend.release_candidate_manifest.get_git_metadata",
                return_value={"commit": None, "branch": None},
            ):
                manifest = build_manifest(root)

            self.assertFalse(manifest["summary"]["passed"])
            self.assertGreater(
                manifest["summary"]["missing_required_files"],
                0,
            )

    def test_manifest_json_is_written(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "manifest.json"

            manifest = {
                "schema_version": "1.0",
                "summary": {"passed": True},
            }

            returned = write_manifest(manifest, output)

            self.assertTrue(returned.exists())

            data = json.loads(
                returned.read_text(encoding="utf-8")
            )

            self.assertEqual(data["schema_version"], "1.0")

    def test_manifest_includes_git_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_project(root)

            with patch(
                "backend.release_candidate_manifest.get_tracked_files",
                return_value=[],
            ), patch(
                "backend.release_candidate_manifest.get_git_metadata",
                return_value={"commit": "abc123", "branch": "main"},
            ):
                manifest = build_manifest(root)

            self.assertEqual(manifest["git"]["commit"], "abc123")
            self.assertEqual(manifest["git"]["branch"], "main")


if __name__ == "__main__":
    unittest.main()
