import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sla_scheduler_retry_preview_router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestRetryPreviewAPI(unittest.TestCase):

    def test_fast_profile_preview(self):
        response = client.get("/api/v1/sla/retry-preview/fast")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["profile"], "fast")

    def test_standard_profile_preview(self):
        response = client.get("/api/v1/sla/retry-preview/standard")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["profile"], "standard")

    def test_conservative_profile_preview(self):
        response = client.get("/api/v1/sla/retry-preview/conservative")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["profile"], "conservative")

    def test_preview_contains_schedule(self):
        response = client.get("/api/v1/sla/retry-preview/standard")
        data = response.json()
        self.assertIn("schedule", data)
        self.assertIn("total_wait_seconds", data)
        self.assertEqual(len(data["schedule"]), data["max_attempts"])

    def test_unknown_profile_returns_404(self):
        response = client.get("/api/v1/sla/retry-preview/unknown")
        self.assertEqual(response.status_code, 404)

    def test_preview_is_read_only_get_endpoint(self):
        response = client.post("/api/v1/sla/retry-preview/standard")
        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    unittest.main()
