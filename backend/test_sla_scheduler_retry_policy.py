import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from sla_scheduler_retry_policy import (
    classify_retry_error,
    should_retry,
)


class TestSLARetryPolicy(unittest.TestCase):

    def test_timeout_is_retryable(self):
        self.assertEqual(
            classify_retry_error(TimeoutError("timeout")),
            "retryable",
        )

    def test_connection_error_is_retryable(self):
        self.assertEqual(
            classify_retry_error(ConnectionError("connection lost")),
            "retryable",
        )

    def test_permission_error_is_permanent(self):
        self.assertEqual(
            classify_retry_error(PermissionError("denied")),
            "permanent",
        )

    def test_value_error_is_permanent(self):
        self.assertEqual(
            classify_retry_error(ValueError("invalid input")),
            "permanent",
        )

    def test_type_error_is_permanent(self):
        self.assertEqual(
            classify_retry_error(TypeError("invalid type")),
            "permanent",
        )

    def test_retry_allowed_before_limit(self):
        self.assertTrue(
            should_retry(TimeoutError(), 1, 3)
        )

    def test_retry_denied_at_attempt_limit(self):
        self.assertFalse(
            should_retry(TimeoutError(), 3, 3)
        )

    def test_permanent_error_never_retries(self):
        self.assertFalse(
            should_retry(ValueError("bad input"), 1, 3)
        )

    def test_invalid_attempt_number(self):
        with self.assertRaises(ValueError):
            should_retry(TimeoutError(), 0, 3)

    def test_invalid_max_attempts(self):
        with self.assertRaises(ValueError):
            should_retry(TimeoutError(), 1, 0)

    def test_boolean_attempt_number_rejected(self):
        with self.assertRaises(TypeError):
            should_retry(TimeoutError(), True, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
