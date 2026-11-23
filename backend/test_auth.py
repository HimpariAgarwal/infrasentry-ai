import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-infrasentry-automated-tests-12345"
os.environ["ADMIN_USERNAME"] = "testadmin"
os.environ["ADMIN_PASSWORD"] = "TestPassword123!"

from fastapi import FastAPI
from fastapi.testclient import TestClient
from auth_router import auth_router

app = FastAPI()
app.include_router(auth_router)

client = TestClient(app)

# Test 1: Protected route without token
response = client.get("/api/v1/auth/me")
assert response.status_code == 401
print("PASS: Unauthenticated request rejected")

# Test 2: Invalid credentials
response = client.post(
    "/api/v1/auth/token",
    data={"username": "wrong", "password": "wrong"},
)
assert response.status_code == 401
print("PASS: Invalid login rejected")

# Test 3: Valid login
response = client.post(
    "/api/v1/auth/token",
    data={
        "username": "testadmin",
        "password": "TestPassword123!",
    },
)
assert response.status_code == 200

token = response.json()["access_token"]
assert response.json()["token_type"] == "bearer"
print("PASS: JWT token generated")

# Test 4: Protected profile
response = client.get(
    "/api/v1/auth/me",
    headers={"Authorization": f"Bearer {token}"},
)
assert response.status_code == 200
assert response.json()["user"] == "testadmin"
print("PASS: Valid JWT accepted")

# Test 5: Protected endpoint
response = client.get(
    "/api/v1/auth/secure-check",
    headers={"Authorization": f"Bearer {token}"},
)
assert response.status_code == 200
print("PASS: Protected endpoint accessible")

# Test 6: Invalid token
response = client.get(
    "/api/v1/auth/me",
    headers={"Authorization": "Bearer invalid-token"},
)
assert response.status_code == 401
print("PASS: Invalid JWT rejected")

print("\nDAY 42 JWT TESTS PASSED")
