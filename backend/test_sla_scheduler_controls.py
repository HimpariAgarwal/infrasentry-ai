import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sla_scheduler_router import router
from sla_scheduler import (
    get_scheduler_status,
    pause_scheduler,
    resume_scheduler,
    start_scheduler,
    stop_scheduler,
)


class TestSLASchedulerControls(unittest.TestCase):

    def setUp(self):
        stop_scheduler()

    def tearDown(self):
        stop_scheduler()

    def client(self):
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def test_scheduler_start_and_pause(self):
        start_scheduler()
        self.assertTrue(get_scheduler_status()["running"])

        pause_scheduler()
        status = get_scheduler_status()

        self.assertTrue(status["running"])
        self.assertTrue(status["paused"])

    def test_scheduler_resume(self):
        start_scheduler()
        pause_scheduler()

        status = resume_scheduler()

        self.assertTrue(status["running"])
        self.assertFalse(status["paused"])

    def test_scheduler_stop(self):
        start_scheduler()
        stop_scheduler()

        self.assertFalse(get_scheduler_status()["running"])

    def test_status_endpoint(self):
        start_scheduler()

        response = self.client().get("/api/v1/sla/scheduler-status")

        self.assertEqual(response.status_code, 200)
        self.assertIn("running", response.json())
        self.assertIn("paused", response.json())

    def test_trigger_requires_running_scheduler(self):
        response = self.client().post("/api/v1/sla/scheduler/trigger")
        self.assertEqual(response.status_code, 409)

    def test_pause_resume_endpoints(self):
        start_scheduler()
        client = self.client()

        pause_response = client.post("/api/v1/sla/scheduler/pause")
        self.assertEqual(pause_response.status_code, 200)
        self.assertTrue(pause_response.json()["paused"])

        resume_response = client.post("/api/v1/sla/scheduler/resume")
        self.assertEqual(resume_response.status_code, 200)
        self.assertFalse(resume_response.json()["paused"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

