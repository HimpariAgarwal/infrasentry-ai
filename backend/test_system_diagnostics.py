import unittest
from collections import namedtuple
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from system_diagnostics import collect_system_diagnostics


DiskUsage = namedtuple("DiskUsage", ["total", "used", "free"])


class TestSystemDiagnostics(unittest.TestCase):

    @patch("system_diagnostics.shutil.disk_usage",
           return_value=DiskUsage(1000, 500, 500))
    def test_healthy_disk_status(self, mock_disk):
        result = collect_system_diagnostics()
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["summary"]["healthy"], 2)

    @patch("system_diagnostics.shutil.disk_usage",
           return_value=DiskUsage(1000, 950, 50))
    def test_low_disk_space_warning(self, mock_disk):
        result = collect_system_diagnostics()
        self.assertEqual(result["status"], "degraded")
        self.assertEqual(result["checks"][0]["status"], "warning")
        self.assertEqual(result["checks"][0]["details"]["usage_percent"], 95.0)

    @patch("system_diagnostics.shutil.disk_usage",
           return_value=DiskUsage(1000, 500, 500))
    def test_custom_disk_threshold(self, mock_disk):
        result = collect_system_diagnostics(disk_warning_threshold=40)
        self.assertEqual(result["status"], "degraded")

    def test_invalid_threshold_rejected(self):
        with self.assertRaises(ValueError):
            collect_system_diagnostics(disk_warning_threshold=101)

    @patch("system_diagnostics.shutil.disk_usage",
           return_value=DiskUsage(1000, 500, 500))
    def test_runtime_information_exists(self, mock_disk):
        result = collect_system_diagnostics()
        self.assertIn("python_version", result["runtime"])
        self.assertIn("platform", result["runtime"])
        self.assertTrue(result["timestamp"])

    @patch("system_diagnostics.shutil.disk_usage",
           return_value=DiskUsage(1000, 500, 500))
    def test_no_sensitive_environment_data(self, mock_disk):
        result = collect_system_diagnostics()
        self.assertNotIn("password", str(result).lower())
        self.assertNotIn("secret_key", str(result).lower())
        self.assertNotIn("jwt_secret", str(result).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
