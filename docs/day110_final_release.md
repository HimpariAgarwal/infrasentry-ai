# Day 110 — Final Audit and Release Preparation

## Release scope

InfraSentry AI includes:
- FastAPI backend and Uvicorn server
- PostgreSQL 16 using Docker Compose
- YOLO-based image detection
- JWT authentication
- Report management APIs
- Image upload and processing
- System readiness and health endpoints
- Dashboard analytics
- Docker health checks and persistent volumes

## Local deployment

```powershell
docker compose up -d --build
docker compose ps
Invoke-RestMethod http://127.0.0.1:8000/health
```

API documentation:
http://127.0.0.1:8000/docs

## Validation

Run:
```powershell
python -m compileall -q backend
python scripts/final_release_audit.py
python scripts/e2e_smoke.py
docker compose config -q
```

## Security checklist

- Keep `.env` files out of Git.
- Never publish JWT secrets or admin credentials.
- Replace local database placeholder credentials before public deployment.
- Restrict database access to the internal Docker network.
- Configure HTTPS and secure reverse proxy before public exposure.
- Review dependencies and update them deliberately.
- Back up PostgreSQL data and uploaded files.

## Release limitations

A successful local health check and E2E test do not certify production
security, model accuracy, scalability or cloud availability.

This release preparation documents the local Docker deployment and
validates the available application workflows.
