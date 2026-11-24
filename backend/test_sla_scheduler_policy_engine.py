import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from sla_scheduler_policy_engine import run_with_retry_policy


class TestSLAPolicyEngine(unittest.TestCase):

    @patch("sla_scheduler_policy_engine.record_retry_run")
    def test_success_on_first_attempt(self, record):
        result = run_with_retry_policy(
            lambda: "completed",
            sleep_func=lambda delay: None,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(result["result"], "completed")
        record.assert_called_once()
        self.assertEqual(record.call_args.kwargs["status"], "success")

    @patch("sla_scheduler_policy_engine.record_retry_run")
    def test_timeout_retries_then_succeeds(self, record):
        calls = {"count": 0}
        delays = []

        def operation():
            calls["count"] += 1
            if calls["count"] < 3:
                raise TimeoutError("temporary timeout")
            return "recovered"

        result = run_with_retry_policy(
            operation,
            initial_delay=2,
            backoff_factor=2,
            sleep_func=delays.append,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["attempts"], 3)
        self.assertEqual(delays, [2, 4])
        self.assertEqual(record.call_args.kwargs["status"], "success")

    @patch("sla_scheduler_policy_engine.record_retry_run")
    def test_permanent_error_stops_immediately(self, record):
        calls = {"count": 0}
        delays = []

        def operation():
            calls["count"] += 1
            raise ValueError("invalid data")

        result = run_with_retry_policy(
            operation,
            sleep_func=delays.append,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(calls["count"], 1)
        self.assertEqual(delays, [])
        self.assertEqual(record.call_args.kwargs["status"], "failed")

    @patch("sla_scheduler_policy_engine.record_retry_run")
    def test_connection_error_exhausts_attempts(self, record):
        calls = {"count": 0}
        delays = []

        def operation():
            calls["count"] += 1
            raise ConnectionError("connection unavailable")

        result = run_with_retry_policy(
            operation,
            max_attempts=3,
            initial_delay=1,
            backoff_factor=2,
            sleep_func=delays.append,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["attempts"], 3)
        self.assertEqual(calls["count"], 3)
        self.assertEqual(delays, [1, 2])

    @patch("sla_scheduler_policy_engine.record_retry_run")
    def test_permission_error_is_not_retried(self, record):
        calls = {"count": 0}

        def operation():
            calls["count"] += 1
            raise PermissionError("access denied")

        result = run_with_retry_policy(
            operation,
            sleep_func=lambda delay: None,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(calls["count"], 1)

    @patch("sla_scheduler_policy_engine.record_retry_run")
    def test_zero_delay_is_supported(self, record):
        calls = {"count": 0}
        delays = []

        def operation():
            calls["count"] += 1
            if calls["count"] == 1:
                raise TimeoutError("retry once")
            return "ok"

        result = run_with_retry_policy(
            operation,
            initial_delay=0,
            sleep_func=delays.append,
        )

        self.assertTrue(result["success"])
        self.assertEqual(delays, [0])

    @patch("sla_scheduler_policy_engine.record_retry_run")
    def test_metrics_failure_does_not_hide_result(self, record):
        record.side_effect = RuntimeError("metrics storage unavailable")

        result = run_with_retry_policy(
            lambda: "ok",
            sleep_func=lambda delay: None,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "ok")

    def test_invalid_max_attempts(self):
        with self.assertRaises(ValueError):
            run_with_retry_policy(lambda: None, max_attempts=0)

    def test_non_callable_operation(self):
        with self.assertRaises(TypeError):
            run_with_retry_policy("not callable")

    def test_invalid_backoff_factor(self):
        with self.assertRaises(ValueError):
            run_with_retry_policy(lambda: None, backoff_factor=0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
