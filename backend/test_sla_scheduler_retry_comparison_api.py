import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sla_scheduler_retry_comparison_router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestRetryComparisonAPI(unittest.TestCase):

    def test_comparison_endpoint(self):
        response = client.get("/api/v1/sla/retry-comparison/")
        self.assertEqual(response.status_code, 200)

    def test_response_contains_three_profiles(self):
        response = client.get("/api/v1/sla/retry-comparison/")
        data = response.json()
        self.assertEqual(data["profiles_compared"], 3)
        self.assertEqual(len(data["profiles"]), 3)

    def test_profile_names_are_correct(self):
        response = client.get("/api/v1/sla/retry-comparison/")
        names = [item["profile"] for item in response.json()["profiles"]]
        self.assertEqual(names, ["fast", "standard", "conservative"])

    def test_post_is_not_allowed(self):
        response = client.post("/api/v1/sla/retry-comparison/")
        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    unittest.main()
