import os
import time
import unittest

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api_access_control import APIAccessControlMiddleware


TEST_SECRET = "infrasentry-day47-test-secret-key-123456"


def create_token(expiration=None):
    payload = {
        "sub": "test-admin",
        "iat": int(time.time()),
        "exp": expiration or int(time.time()) + 300,
    }
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")


def create_test_app():
    app = FastAPI()
    app.add_middleware(APIAccessControlMiddleware)

    @app.get("/api/v1/detect")
    def protected_endpoint():
        return {"message": "Protected access granted"}

    @app.get("/health")
    def public_endpoint():
        return {"status": "healthy"}

    return app


class TestAPIAccessControl(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ["JWT_SECRET_KEY"] = TEST_SECRET
        cls.client = TestClient(create_test_app())

    def test_missing_token_rejected(self):
        response = self.client.get("/api/v1/detect")
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_rejected(self):
        response = self.client.get(
            "/api/v1/detect",
            headers={"Authorization": "Bearer invalid-token"},
        )
        self.assertEqual(response.status_code, 401)

    def test_valid_token_accepted(self):
        token = create_token()
        response = self.client.get(
            "/api/v1/detect",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"],
            "Protected access granted",
        )

    def test_expired_token_rejected(self):
        token = create_token(int(time.time()) - 60)
        response = self.client.get(
            "/api/v1/detect",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 401)

    def test_public_endpoint_remains_accessible(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_missing_secret_returns_service_unavailable(self):
        os.environ["JWT_SECRET_KEY"] = ""
        try:
            response = self.client.get(
                "/api/v1/detect",
                headers={"Authorization": f"Bearer {create_token()}"},
            )
            self.assertEqual(response.status_code, 503)
        finally:
            os.environ["JWT_SECRET_KEY"] = TEST_SECRET


if __name__ == "__main__":
    unittest.main(verbosity=2)
