import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.sla_scheduler import (
    start_sla_scheduler,
    stop_sla_scheduler,
    get_sla_scheduler_status,
    run_sla_escalation_job,
)
from backend.sla_scheduler_router import router


class TestSLAScheduler(unittest.TestCase):

    def tearDown(self):
        stop_sla_scheduler()

    def test_scheduler_initially_stopped(self):
        stop_sla_scheduler()
        status = get_sla_scheduler_status()
        self.assertFalse(status["running"])
        self.assertEqual(status["interval_seconds"], 60)

    def test_scheduler_starts(self):
        start_sla_scheduler()
        status = get_sla_scheduler_status()
        self.assertTrue(status["running"])
        self.assertEqual(status["interval_seconds"], 60)

    def test_scheduler_start_is_idempotent(self):
        start_sla_scheduler()
        first_status = get_sla_scheduler_status()

        start_sla_scheduler()
        second_status = get_sla_scheduler_status()

        self.assertTrue(first_status["running"])
        self.assertTrue(second_status["running"])

    def test_scheduler_stops(self):
        start_sla_scheduler()
        stop_sla_scheduler()

        status = get_sla_scheduler_status()
        self.assertFalse(status["running"])

    @patch("backend.sla_scheduler.generate_sla_alerts")
    def test_job_calls_alert_generator(self, mock_generate):
        mock_generate.return_value = {"generated": 2}

        run_sla_escalation_job()

        mock_generate.assert_called_once()

    @patch("backend.sla_scheduler.generate_sla_alerts")
    def test_job_handles_generator_error(self, mock_generate):
        mock_generate.side_effect = RuntimeError("Test failure")

        # Job should log the exception without crashing the test.
        run_sla_escalation_job()

        mock_generate.assert_called_once()

    def test_scheduler_status_api(self):
        app = FastAPI()
        app.include_router(router)

        with TestClient(app) as client:
            response = client.get("/api/v1/sla/scheduler-status")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("running", data)
        self.assertEqual(data["interval_seconds"], 60)


if __name__ == "__main__":
    unittest.main(verbosity=2)
