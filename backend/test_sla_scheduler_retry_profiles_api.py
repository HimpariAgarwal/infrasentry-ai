import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sla_scheduler_retry_profiles_router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestSLARetryProfilesAPI(unittest.TestCase):

    def test_list_profiles(self):
        response = client.get("/api/v1/sla/retry-profiles")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 3)
        self.assertEqual(
            {item["name"] for item in data["profiles"]},
            {"fast", "standard", "conservative"},
        )

    def test_fast_profile(self):
        response = client.get("/api/v1/sla/retry-profiles/fast")

        self.assertEqual(response.status_code, 200)
        profile = response.json()["profile"]
        self.assertEqual(profile["max_attempts"], 2)
        self.assertEqual(profile["initial_delay"], 0.5)

    def test_standard_profile(self):
        response = client.get("/api/v1/sla/retry-profiles/standard")

        self.assertEqual(response.status_code, 200)
        profile = response.json()["profile"]
        self.assertEqual(profile["max_attempts"], 3)
        self.assertEqual(profile["initial_delay"], 1)

    def test_conservative_profile(self):
        response = client.get("/api/v1/sla/retry-profiles/conservative")

        self.assertEqual(response.status_code, 200)
        profile = response.json()["profile"]
        self.assertEqual(profile["max_attempts"], 3)
        self.assertEqual(profile["initial_delay"], 3)

    def test_profile_lookup_is_case_insensitive(self):
        response = client.get("/api/v1/sla/retry-profiles/STANDARD")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["profile"]["name"], "standard")

    def test_unknown_profile_returns_404(self):
        response = client.get("/api/v1/sla/retry-profiles/unknown")

        self.assertEqual(response.status_code, 404)

    def test_wrong_method_returns_405(self):
        response = client.post("/api/v1/sla/retry-profiles")

        self.assertEqual(response.status_code, 405)

    def test_response_contains_all_configuration_fields(self):
        response = client.get("/api/v1/sla/retry-profiles/standard")
        profile = response.json()["profile"]

        for field in (
            "name",
            "max_attempts",
            "initial_delay",
            "backoff_factor",
        ):
            self.assertIn(field, profile)


if __name__ == "__main__":
    unittest.main(verbosity=2)
