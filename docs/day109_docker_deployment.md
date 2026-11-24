# Day 109 — Docker Deployment

## Architecture
- FastAPI backend served by Uvicorn.
- PostgreSQL 16 database.
- Docker Compose manages the backend and database.
- YOLO model weights are copied into the backend image.
- Docker named volumes persist PostgreSQL data, uploads, and processed files.
- Backend configuration is supplied through `backend/.env` at runtime.

## Requirements
- Docker Desktop with WSL 2 integration.
- `backend/.env` configured with the required application secrets.

## Start
```powershell
docker compose up -d --build
docker compose ps
```

## Verify
```powershell
docker compose ps
docker compose logs --tail 100 backend
Invoke-RestMethod http://127.0.0.1:8000/health
python scripts/e2e_smoke.py
```

Expected API health response includes:
`status: healthy` and `project: InfraSentry AI`.

## Stop
```powershell
docker compose down
```

To remove persistent database and uploaded data volumes as well:
```powershell
docker compose down -v
```
Warning: `-v` permanently deletes the named Docker volumes.

## Services
- Backend: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs
- PostgreSQL: internal Compose service `db`, port 5432.

## Security notes
- Never commit `backend/.env` or expose its secrets.
- The Compose database password is a local-development placeholder.
- Replace local credentials, configure strong secrets, restrict network exposure,
  and use HTTPS before any public or production deployment.
- This configuration is intended for local Docker deployment, not production
  security certification.
