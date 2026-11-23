# Day 44 - Backend JWT API Protection

## Protected endpoints

- POST /api/v1/detect
- GET /api/v1/history
- GET /api/v1/history/{record_id}
- DELETE /api/v1/history/{record_id}
- GET /api/v1/logs
- GET /api/v1/logs/export
- DELETE /api/v1/logs
- GET /api/v1/system-health

## Authentication

Protected endpoints require:

Authorization: Bearer <JWT_TOKEN>

JWT tokens are validated using the JWT_SECRET_KEY environment variable.
The middleware accepts HS256 tokens with a subject and valid expiry.

## Public endpoints

Authentication token creation and other non-protected endpoints remain accessible.

## Security behavior

- Missing token: HTTP 401
- Invalid token: HTTP 401
- Expired token: HTTP 401
- Missing or invalid server secret: HTTP 503

This is prototype-level access control, not a complete production security system.
