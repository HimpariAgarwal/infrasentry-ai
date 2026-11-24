import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from sla_scheduler_retry_execution import execute_sla_generation_with_retry


class TestSLARetryExecution(unittest.TestCase):

    @patch("sla_scheduler_retry_execution.record_retry_run")
    @patch("sla_scheduler_retry_execution.run_with_retries")
    def test_successful_execution_records_success(self, retry, record):
        retry.return_value = {
            "success": True,
            "attempts": 2,
            "result": {"created": 3},
        }
        generator = lambda: {"created": 3}

        result = execute_sla_generation_with_retry(generator)

        self.assertEqual(result, {"created": 3})
        retry.assert_called_once()
        self.assertEqual(retry.call_args.kwargs["max_attempts"], 3)
        self.assertEqual(record.call_args.kwargs["status"], "success")
        self.assertEqual(record.call_args.kwargs["attempts"], 2)

    @patch("sla_scheduler_retry_execution.record_retry_run")
    @patch("sla_scheduler_retry_execution.run_with_retries")
    def test_failed_execution_records_failure_and_raises(self, retry, record):
        retry.return_value = {
            "success": False,
            "attempts": 3,
            "error": "temporary database failure",
        }

        with self.assertRaises(RuntimeError):
            execute_sla_generation_with_retry(lambda: None)

        self.assertEqual(record.call_args.kwargs["status"], "failed")
        self.assertEqual(record.call_args.kwargs["attempts"], 3)
        self.assertIn("database failure", record.call_args.kwargs["error"])

    @patch("sla_scheduler_retry_execution.record_retry_run")
    @patch("sla_scheduler_retry_execution.run_with_retries")
    def test_unexpected_exception_is_recorded_and_raised(self, retry, record):
        retry.side_effect = RuntimeError("unexpected failure")

        with self.assertRaisesRegex(RuntimeError, "unexpected failure"):
            execute_sla_generation_with_retry(lambda: None)

        self.assertEqual(record.call_args.kwargs["status"], "failed")
        self.assertIn("unexpected failure", record.call_args.kwargs["error"])

    @patch("sla_scheduler_retry_execution.record_retry_run")
    @patch("sla_scheduler_retry_execution.run_with_retries")
    def test_generator_is_passed_to_retry_helper(self, retry, record):
        retry.return_value = {"success": True, "attempts": 1, "result": "ok"}
        generator = lambda: "ok"

        execute_sla_generation_with_retry(generator)

        self.assertIs(retry.call_args.args[0], generator)

    def test_scheduler_calls_retry_execution(self):
        scheduler = ROOT / "backend" / "sla_scheduler.py"
        source = scheduler.read_text(encoding="utf-8-sig")
        self.assertIn(
            "execute_sla_generation_with_retry(generate_sla_alerts)",
            source,
        )
        self.assertIn(
            "from sla_scheduler_retry_execution import execute_sla_generation_with_retry",
            source,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
