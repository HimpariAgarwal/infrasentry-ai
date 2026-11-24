import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sla_scheduler_router import router


class TestSLASchedulerControlsAPI(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    def test_status_endpoint(self):
        response = self.client.get("/api/v1/sla/scheduler-status")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    @patch("sla_scheduler_router.start_scheduler")
    def test_start_endpoint(self, mock_function):
        mock_function.return_value = {"status": "started"}
        response = self.client.post("/api/v1/sla/scheduler/start")
        self.assertEqual(response.status_code, 200)
        mock_function.assert_called_once()

    @patch("sla_scheduler_router.pause_scheduler")
    def test_pause_endpoint(self, mock_function):
        mock_function.return_value = {"status": "paused"}
        response = self.client.post("/api/v1/sla/scheduler/pause")
        self.assertEqual(response.status_code, 200)
        mock_function.assert_called_once()

    @patch("sla_scheduler_router.resume_scheduler")
    def test_resume_endpoint(self, mock_function):
        mock_function.return_value = {"status": "resumed"}
        response = self.client.post("/api/v1/sla/scheduler/resume")
        self.assertEqual(response.status_code, 200)
        mock_function.assert_called_once()

    @patch("sla_scheduler_router.stop_scheduler")
    def test_stop_endpoint(self, mock_function):
        mock_function.return_value = {"status": "stopped"}
        response = self.client.post("/api/v1/sla/scheduler/stop")
        self.assertEqual(response.status_code, 200)
        mock_function.assert_called_once()

    @patch("sla_scheduler_router.trigger_scheduler_now")
    def test_trigger_endpoint(self, mock_function):
        mock_function.return_value = {"status": "triggered"}
        response = self.client.post("/api/v1/sla/scheduler/trigger")
        self.assertEqual(response.status_code, 200)
        mock_function.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
