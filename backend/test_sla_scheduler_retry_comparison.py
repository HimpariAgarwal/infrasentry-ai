import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from sla_scheduler_retry_comparison import compare_retry_profiles


class TestRetryComparison(unittest.TestCase):

    def test_all_profiles_are_returned(self):
        result = compare_retry_profiles()
        names = [item["profile"] for item in result["profiles"]]
        self.assertEqual(names, ["fast", "standard", "conservative"])

    def test_profile_count_is_correct(self):
        result = compare_retry_profiles()
        self.assertEqual(result["profiles_compared"], 3)

    def test_each_profile_has_required_fields(self):
        result = compare_retry_profiles()
        required = {
            "profile", "max_attempts", "initial_delay",
            "backoff_factor", "total_wait_seconds",
        }
        for profile in result["profiles"]:
            self.assertTrue(required.issubset(profile.keys()))

    def test_wait_times_are_non_negative(self):
        result = compare_retry_profiles()
        for profile in result["profiles"]:
            self.assertGreaterEqual(profile["total_wait_seconds"], 0)

    def test_comparison_is_read_only(self):
        first = compare_retry_profiles()
        second = compare_retry_profiles()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
