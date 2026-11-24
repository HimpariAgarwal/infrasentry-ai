import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from sla_scheduler_retry_profiles import get_retry_profile
from sla_scheduler_retry_preview import build_retry_preview


class TestRetryPreview(unittest.TestCase):

    def test_first_attempt_has_zero_delay(self):
        profile = get_retry_profile("fast")
        result = build_retry_preview(profile)
        self.assertEqual(
            result["schedule"][0]["delay_before_attempt_seconds"], 0.0
        )

    def test_attempt_count_matches_profile(self):
        profile = get_retry_profile("standard")
        result = build_retry_preview(profile)
        self.assertEqual(
            len(result["schedule"]), profile.max_attempts
        )

    def test_exponential_backoff_values(self):
        profile = get_retry_profile("standard")
        result = build_retry_preview(profile)
        delays = [
            item["delay_before_attempt_seconds"]
            for item in result["schedule"]
        ]
        expected = [
            0.0,
            profile.initial_delay,
            profile.initial_delay * profile.backoff_factor,
        ]
        self.assertEqual(delays, expected)

    def test_cumulative_wait_is_correct(self):
        profile = get_retry_profile("standard")
        result = build_retry_preview(profile)
        expected = sum(
            item["delay_before_attempt_seconds"]
            for item in result["schedule"]
        )
        self.assertEqual(result["total_wait_seconds"], expected)

    def test_attempt_numbers_are_sequential(self):
        profile = get_retry_profile("conservative")
        result = build_retry_preview(profile)
        numbers = [item["attempt"] for item in result["schedule"]]
        self.assertEqual(
            numbers, list(range(1, profile.max_attempts + 1))
        )

    def test_preview_does_not_modify_profile(self):
        profile = get_retry_profile("fast")
        original = (
            profile.name,
            profile.max_attempts,
            profile.initial_delay,
            profile.backoff_factor,
        )
        build_retry_preview(profile)
        current = (
            profile.name,
            profile.max_attempts,
            profile.initial_delay,
            profile.backoff_factor,
        )
        self.assertEqual(original, current)


if __name__ == "__main__":
    unittest.main()
