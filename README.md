# InfraSentry AI


## Docker Deployment

InfraSentry AI can be run locally using Docker Compose.

### Architecture
- FastAPI backend with Uvicorn
- PostgreSQL 16 database
- AI image detection using YOLO
- Persistent Docker volumes for database and image data

### Run locally
```powershell
docker compose up -d --build
docker compose ps
```

### Verify API
```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

API documentation: http://127.0.0.1:8000/docs

### Stop
```powershell
docker compose down
```

See [Day 109 Docker Deployment](docs/day109_docker_deployment.md)
for configuration and deployment details.

## Project Highlights

- JWT-based authentication
- Report creation, update and deletion
- Image upload and processing
- AI detection API
- System readiness and health monitoring
- Dashboard analytics
- Dockerized backend and PostgreSQL

## Deployment Scope

This repository currently demonstrates local Docker deployment.
Production use requires hardened credentials, HTTPS, restricted network
access, production database configuration and operational monitoring.
