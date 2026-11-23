import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from security_headers import SecurityHeadersMiddleware
from rate_limit import RateLimitMiddleware

app = FastAPI()

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=3,
    window_seconds=60,
)

@app.get("/api/test")
def test_endpoint():
    return {"success": True}

@app.get("/health")
def health_endpoint():
    return {"status": "healthy"}

client = TestClient(app)

# Test 1: API endpoint
response = client.get("/api/test")
assert response.status_code == 200
print("PASS: API endpoint responds successfully")

# Test 2: Security headers
assert response.headers.get("X-Content-Type-Options") == "nosniff"
assert response.headers.get("X-Frame-Options") == "DENY"
assert response.headers.get("Referrer-Policy") is not None
print("PASS: Security headers are present")

# Test 3: Rate limit
client.get("/api/test")
client.get("/api/test")
blocked = client.get("/api/test")

assert blocked.status_code == 429
assert blocked.headers.get("Retry-After") is not None
print("PASS: Rate limit blocks excessive requests")

# Test 4: Non-API route is not rate limited
for _ in range(5):
    result = client.get("/health")
    assert result.status_code == 200

print("PASS: Non-API health route remains accessible")
print("\nDAY 41 SECURITY TESTS PASSED")
