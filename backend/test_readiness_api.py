import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

import system_router


class TestReadinessAPI(unittest.TestCase):

    def setUp(self):
        self.app = FastAPI()

        router = next(
            value for value in vars(system_router).values()
            if isinstance(value, APIRouter)
        )

        self.app.include_router(router)
        self.client = TestClient(self.app)

    def authenticate(self):
        self.app.dependency_overrides[
            system_router.get_current_user
        ] = lambda: {"username": "readiness-test"}

    def test_unauthorized_request_rejected(self):
        response = self.client.get("/api/v1/readiness")
        self.assertEqual(response.status_code, 401)

    def test_healthy_system_reports_ready(self):
        self.authenticate()

        diagnostics = {
            "service": "InfraSentry AI",
            "status": "healthy",
            "timestamp": "2026-11-24T10:00:00Z",
            "summary": {
                "total": 2,
                "healthy": 2,
                "degraded": 0,
            },
        }

        with patch.object(
            system_router,
            "collect_system_diagnostics",
            return_value=diagnostics,
        ):
            response = self.client.get("/api/v1/readiness")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ready"])
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["checks"]["healthy"], 2)
        self.assertEqual(data["checks"]["degraded"], 0)

    def test_degraded_system_reports_not_ready(self):
        self.authenticate()

        diagnostics = {
            "service": "InfraSentry AI",
            "status": "degraded",
            "timestamp": "2026-11-24T10:00:00Z",
            "summary": {
                "total": 2,
                "healthy": 1,
                "degraded": 1,
            },
        }

        with patch.object(
            system_router,
            "collect_system_diagnostics",
            return_value=diagnostics,
        ):
            response = self.client.get("/api/v1/readiness")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["ready"])
        self.assertEqual(data["status"], "degraded")
        self.assertEqual(data["checks"]["degraded"], 1)


if __name__ == "__main__":
    unittest.main()
