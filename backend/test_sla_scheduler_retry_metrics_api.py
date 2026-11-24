import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sla_scheduler_retry_metrics_router import router


class TestRetryMetricsAPI(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    @patch("sla_scheduler_retry_metrics_router.get_retry_metrics")
    def test_returns_metrics(self, mock_metrics):
        mock_metrics.return_value = {
            "total_runs": 5,
            "successful_runs": 4,
            "failed_runs": 1,
            "total_attempts": 7,
            "average_duration_seconds": 1.25,
            "last_run": None,
            "history": [],
        }

        response = self.client.get("/api/v1/sla/retry-metrics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_runs"], 5)
        self.assertEqual(response.json()["failed_runs"], 1)

    @patch("sla_scheduler_retry_metrics_router.get_retry_metrics")
    def test_returns_empty_metrics(self, mock_metrics):
        mock_metrics.return_value = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "total_attempts": 0,
            "average_duration_seconds": 0.0,
            "last_run": None,
            "history": [],
        }

        response = self.client.get("/api/v1/sla/retry-metrics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["history"], [])

    @patch("sla_scheduler_retry_metrics_router.get_retry_metrics")
    def test_handles_metrics_error(self, mock_metrics):
        mock_metrics.side_effect = OSError("storage unavailable")

        response = self.client.get("/api/v1/sla/retry-metrics")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()["detail"],
            "Unable to retrieve SLA retry metrics"
        )

    def test_endpoint_method(self):
        response = self.client.post("/api/v1/sla/retry-metrics")
        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    unittest.main(verbosity=2)
