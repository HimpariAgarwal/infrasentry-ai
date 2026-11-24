import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "backend"))

import sla_scheduler_retry_metrics as metrics


class TestSchedulerRetryMetrics(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.metrics_file = Path(self.temp_dir.name) / "retry_metrics.json"
        self.patch_file = patch.object(metrics, "METRICS_FILE", self.metrics_file)
        self.patch_file.start()

    def tearDown(self):
        self.patch_file.stop()
        self.temp_dir.cleanup()

    def test_empty_metrics_default(self):
        data = metrics.get_retry_metrics()
        self.assertEqual(data["total_runs"], 0)
        self.assertEqual(data["history"], [])

    def test_records_successful_run(self):
        data = metrics.record_retry_run("success", 2, 1.5)
        self.assertEqual(data["successful_runs"], 1)
        self.assertEqual(data["failed_runs"], 0)
        self.assertEqual(data["total_attempts"], 2)

    def test_records_failed_run(self):
        data = metrics.record_retry_run(
            "failed", 3, 2.5, error="temporary failure"
        )
        self.assertEqual(data["failed_runs"], 1)
        self.assertEqual(data["last_run"]["error"], "temporary failure")

    def test_average_duration(self):
        metrics.record_retry_run("success", 1, 2.0)
        data = metrics.record_retry_run("failed", 2, 4.0)
        self.assertEqual(data["average_duration_seconds"], 3.0)

    def test_persists_metrics(self):
        metrics.record_retry_run("success", 1, 0.5)
        loaded = metrics.get_retry_metrics()
        self.assertEqual(loaded["total_runs"], 1)
        self.assertEqual(len(loaded["history"]), 1)

    def test_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            metrics.record_retry_run("unknown", 1, 1.0)
        with self.assertRaises(ValueError):
            metrics.record_retry_run("success", 0, 1.0)
        with self.assertRaises(ValueError):
            metrics.record_retry_run("success", 1, -1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
