import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from sla_scheduler_retry_profiles import (
    RetryProfile,
    get_retry_profile,
    execute_with_profile,
)


class TestSLARetryProfiles(unittest.TestCase):

    def test_fast_profile(self):
        profile = get_retry_profile("fast")
        self.assertEqual(profile.max_attempts, 2)
        self.assertEqual(profile.initial_delay, 0.5)

    def test_standard_profile(self):
        profile = get_retry_profile("standard")
        self.assertEqual(profile.max_attempts, 3)
        self.assertEqual(profile.initial_delay, 1)

    def test_conservative_profile(self):
        profile = get_retry_profile("conservative")
        self.assertEqual(profile.max_attempts, 3)
        self.assertEqual(profile.initial_delay, 3)
        self.assertEqual(profile.backoff_factor, 3)

    def test_profile_name_is_case_insensitive(self):
        self.assertEqual(
            get_retry_profile("STANDARD"),
            get_retry_profile("standard"),
        )

    def test_unknown_profile_rejected(self):
        with self.assertRaises(ValueError):
            get_retry_profile("turbo")

    def test_non_string_profile_rejected(self):
        with self.assertRaises(TypeError):
            get_retry_profile(None)

    def test_invalid_attempt_count_rejected(self):
        with self.assertRaises(ValueError):
            RetryProfile("invalid", 0, 1, 2)

    def test_negative_delay_rejected(self):
        with self.assertRaises(ValueError):
            RetryProfile("invalid", 2, -1, 2)

    def test_backoff_below_one_rejected(self):
        with self.assertRaises(ValueError):
            RetryProfile("invalid", 2, 1, 0.5)

    def test_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            RetryProfile(" ", 2, 1, 2)

    @patch("sla_scheduler_retry_profiles.run_with_retry_policy")
    def test_standard_profile_passes_configuration(self, engine):
        engine.return_value = {"success": True, "attempts": 1}

        result = execute_with_profile(
            lambda: "ok",
            profile_name="standard",
            sleep_func=lambda delay: None,
        )

        self.assertTrue(result["success"])
        self.assertEqual(engine.call_args.kwargs["max_attempts"], 3)
        self.assertEqual(engine.call_args.kwargs["initial_delay"], 1)
        self.assertEqual(engine.call_args.kwargs["backoff_factor"], 2)
        self.assertIn("sleep_func", engine.call_args.kwargs)

    @patch("sla_scheduler_retry_profiles.run_with_retry_policy")
    def test_default_profile_is_standard(self, engine):
        engine.return_value = {"success": True}

        execute_with_profile(lambda: "ok")

        self.assertEqual(engine.call_args.kwargs["max_attempts"], 3)
        self.assertEqual(engine.call_args.kwargs["initial_delay"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
