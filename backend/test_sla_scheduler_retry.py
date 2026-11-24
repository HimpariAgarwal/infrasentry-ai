import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "backend"))

from sla_scheduler_retry import run_with_retries


class TestSchedulerRetry(unittest.TestCase):

    def test_success_first_attempt(self):
        job = Mock(return_value="completed")

        result = run_with_retries(job, sleep_func=lambda _: None)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(result["result"], "completed")
        job.assert_called_once()

    def test_success_after_retry(self):
        job = Mock(side_effect=[
            RuntimeError("temporary"),
            "completed"
        ])
        delays = []

        result = run_with_retries(
            job,
            max_attempts=3,
            initial_delay=2,
            sleep_func=delays.append,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(delays, [2])

    def test_all_attempts_fail(self):
        job = Mock(side_effect=RuntimeError("service unavailable"))
        delays = []

        result = run_with_retries(
            job,
            max_attempts=3,
            initial_delay=1,
            sleep_func=delays.append,
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["attempts"], 3)
        self.assertEqual(result["error"], "service unavailable")
        self.assertEqual(delays, [1, 2])

    def test_backoff_multiplier(self):
        job = Mock(side_effect=[
            RuntimeError("one"),
            RuntimeError("two"),
            "done"
        ])
        delays = []

        run_with_retries(
            job,
            max_attempts=3,
            initial_delay=1,
            backoff_factor=3,
            sleep_func=delays.append,
        )

        self.assertEqual(delays, [1, 3])

    def test_invalid_attempt_count(self):
        with self.assertRaises(ValueError):
            run_with_retries(lambda: None, max_attempts=0)

    def test_invalid_delay(self):
        with self.assertRaises(ValueError):
            run_with_retries(lambda: None, initial_delay=-1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
