import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "backend"))

import sla_scheduler


class TestSchedulerReliabilityIntegration(unittest.TestCase):

    def test_scheduler_job_has_reliability_wrapper(self):
        self.assertTrue(
            hasattr(sla_scheduler._run_sla_job, "__wrapped__"),
            "_run_sla_job must use the reliability decorator"
        )

    def test_original_job_function_is_preserved(self):
        original = sla_scheduler._run_sla_job.__wrapped__
        self.assertTrue(callable(original))
        self.assertEqual(original.__name__, "_run_sla_job")


if __name__ == "__main__":
    unittest.main(verbosity=2)
