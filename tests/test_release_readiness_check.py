import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.release_readiness_check import (
    check_docker_compose,
    check_required_files,
    check_tracked_sensitive_files,
    is_sensitive_path,
    run_readiness,
)


class ReleaseReadinessTests(unittest.TestCase):

    def test_required_files_detect_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            passed, message = check_required_files(Path(directory))
            self.assertFalse(passed)
            self.assertIn("Missing files", message)

    def test_required_files_all_present(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            from scripts.release_readiness_check import REQUIRED_FILES

            for name in REQUIRED_FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("test", encoding="utf-8")

            passed, message = check_required_files(root)
            self.assertTrue(passed)
            self.assertIn("required files exist", message)

    def test_env_file_is_sensitive(self):
        self.assertTrue(is_sensitive_path("backend/.env"))

    def test_env_example_is_allowed(self):
        self.assertFalse(is_sensitive_path("backend/.env.example"))

    def test_private_key_is_sensitive(self):
        self.assertTrue(is_sensitive_path("certificates/private.pem"))

    def test_backup_directory_is_sensitive(self):
        self.assertTrue(is_sensitive_path("backups/old/main.py"))

    @patch("scripts.release_readiness_check.subprocess.run")
    def test_tracked_sensitive_file_detected(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="README.md\0backend/.env\0",
            stderr="",
        )

        passed, message = check_tracked_sensitive_files(Path("."))

        self.assertFalse(passed)
        self.assertIn("backend/.env", message)

    @patch("scripts.release_readiness_check.subprocess.run")
    def test_safe_tracked_files_pass(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="README.md\0backend/.env.example\0",
            stderr="",
        )

        passed, message = check_tracked_sensitive_files(Path("."))

        self.assertTrue(passed)
        self.assertIn("no sensitive paths", message)

    @patch("scripts.release_readiness_check.subprocess.run")
    def test_docker_compose_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )

        passed, message = check_docker_compose(Path("."))

        self.assertTrue(passed)
        self.assertIn("valid", message)

    @patch("scripts.release_readiness_check.subprocess.run")
    def test_docker_compose_failure(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="Invalid compose file"
        )

        passed, message = check_docker_compose(Path("."))

        self.assertFalse(passed)
        self.assertIn("Invalid compose file", message)

    @patch("scripts.release_readiness_check.subprocess.run")
    def test_readiness_can_skip_docker(self, mock_run):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            from scripts.release_readiness_check import REQUIRED_FILES

            for name in REQUIRED_FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("test", encoding="utf-8")

            mock_run.return_value = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="README.md\0",
                stderr="",
            )

            passed, checks = run_readiness(root, skip_docker=True)

            self.assertTrue(passed)
            self.assertEqual(len(checks), 2)
            self.assertEqual(mock_run.call_count, 1)


if __name__ == "__main__":
    unittest.main()
