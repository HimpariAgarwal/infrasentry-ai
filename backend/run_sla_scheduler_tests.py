import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.test_sla_scheduler import TestSLAScheduler

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSLAScheduler)
result = unittest.TestResult()
suite.run(result)

report = {
    "test_suite": "SLA Scheduler Reliability",
    "total_tests": result.testsRun,
    "passed": result.testsRun - len(result.failures) - len(result.errors),
    "failed": len(result.failures),
    "errors": len(result.errors),
    "success": result.wasSuccessful(),
    "failures": [
        {"test": test.id(), "message": message}
        for test, message in result.failures
    ],
    "errors_detail": [
        {"test": test.id(), "message": message}
        for test, message in result.errors
    ],
}

output = ROOT / "reports" / "day65_sla_scheduler_test_report.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding="utf-8")

print(json.dumps(report, indent=2))

if not result.wasSuccessful():
    raise SystemExit("SLA scheduler tests failed.")
