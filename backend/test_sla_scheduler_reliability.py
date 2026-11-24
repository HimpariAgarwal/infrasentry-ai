import sys
import time
import unittest
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "backend"))

from sla_scheduler_reliability import prevent_overlapping_runs


class TestSchedulerReliability(unittest.TestCase):

    def test_successful_execution(self):
        @prevent_overlapping_runs
        def job():
            return "completed"

        result = job()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], "completed")
        self.assertGreaterEqual(result["duration_seconds"], 0)

    def test_exception_recovery(self):
        @prevent_overlapping_runs
        def job():
            raise ValueError("Test failure")

        result = job()
        self.assertEqual(result["status"], "failed")
        self.assertIn("Test failure", result["error"])

    def test_lock_released_after_failure(self):
        @prevent_overlapping_runs
        def job():
            raise RuntimeError("Temporary error")

        first = job()
        second = job()

        self.assertEqual(first["status"], "failed")
        self.assertEqual(second["status"], "failed")

    def test_prevents_overlapping_execution(self):
        started = threading.Event()
        release = threading.Event()
        results = []

        @prevent_overlapping_runs
        def job():
            started.set()
            release.wait(timeout=3)
            return "finished"

        worker = threading.Thread(target=lambda: results.append(job()))
        worker.start()

        self.assertTrue(started.wait(timeout=2))
        second = job()

        self.assertEqual(second["status"], "skipped")

        release.set()
        worker.join(timeout=4)

        self.assertFalse(worker.is_alive())
        self.assertEqual(results[0]["status"], "success")

    def test_execution_lock_reusable(self):
        @prevent_overlapping_runs
        def job():
            return "ok"

        self.assertEqual(job()["status"], "success")
        self.assertEqual(job()["status"], "success")


if __name__ == "__main__":
    unittest.main(verbosity=2)
