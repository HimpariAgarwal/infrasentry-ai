import sys
from pathlib import Path
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from auth_router import get_current_user
import system_router


def create_test_app(authenticated=False):
    app = FastAPI()
    app.include_router(system_router.router)

    if authenticated:
        app.dependency_overrides[get_current_user] = (
            lambda: {"username": "test-admin"}
        )

    return app


class TestSystemDiagnosticsAPI(unittest.TestCase):

    def test_unauthorized_access_rejected(self):
        client = TestClient(create_test_app())

        response = client.get("/api/v1/system-diagnostics")

        self.assertEqual(response.status_code, 401)

    @patch(
        "system_router.collect_system_diagnostics",
        return_value={
            "service": "InfraSentry AI",
            "status": "healthy",
            "checks": [],
            "summary": {
                "total": 0,
                "healthy": 0,
                "degraded": 0,
            },
        },
    )
    def test_authenticated_access_successful(self, mock_diagnostics):
        client = TestClient(create_test_app(authenticated=True))

        response = client.get("/api/v1/system-diagnostics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
        self.assertEqual(response.json()["service"], "InfraSentry AI")
        mock_diagnostics.assert_called_once()

    @patch(
        "system_router.collect_system_diagnostics",
        side_effect=OSError("Internal diagnostic failure"),
    )
    def test_internal_error_handled_safely(self, mock_diagnostics):
        client = TestClient(create_test_app(authenticated=True))

        response = client.get("/api/v1/system-diagnostics")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()["detail"],
            "System diagnostics unavailable.",
        )
        self.assertNotIn(
            "Internal diagnostic failure",
            response.text,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
