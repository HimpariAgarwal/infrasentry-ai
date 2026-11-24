import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "backend"))

from sla_scheduler_retry import run_with_retries


class TestSchedulerRetryPolicy(unittest.TestCase):

    def test_single_attempt_failure(self):
        job = Mock(side_effect=RuntimeError("failure"))

        result = run_with_retries(
            job,
            max_attempts=1,
            sleep_func=lambda _: None
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["attempts"], 1)
        job.assert_called_once()

    def test_zero_delay_retry(self):
        job = Mock(side_effect=[RuntimeError("temporary"), "done"])
        delays = []

        result = run_with_retries(
            job,
            max_attempts=2,
            initial_delay=0,
            sleep_func=delays.append
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(delays, [0])

    def test_custom_backoff_sequence(self):
        job = Mock(side_effect=[
            RuntimeError("first"),
            RuntimeError("second"),
            RuntimeError("third"),
            "done"
        ])
        delays = []

        result = run_with_retries(
            job,
            max_attempts=4,
            initial_delay=2,
            backoff_factor=2,
            sleep_func=delays.append
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(delays, [2, 4, 8])

    def test_job_called_exact_number_of_attempts(self):
        job = Mock(side_effect=RuntimeError("failed"))

        result = run_with_retries(
            job,
            max_attempts=4,
            sleep_func=lambda _: None
        )

        self.assertEqual(result["attempts"], 4)
        self.assertEqual(job.call_count, 4)

    def test_result_contains_expected_fields(self):
        result = run_with_retries(
            lambda: "success",
            sleep_func=lambda _: None
        )

        self.assertEqual(
            set(result.keys()),
            {"status", "attempts", "result", "error"}
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
