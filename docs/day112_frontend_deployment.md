# Day 112 - Frontend Production Deployment

## Objective

Deploy the React + Vite frontend through a production Nginx
container and connect it to the existing FastAPI backend.

## Architecture

Browser
  |
  | HTTP :3000
  v
Nginx / React static build
  |
  | /api/*
  v
FastAPI backend :8000
  |
  v
PostgreSQL :5432

## Implementation

- Multi-stage Node.js frontend image.
- Production static assets served by Nginx.
- Nginx reverse proxy for /api/ requests.
- SPA fallback to index.html.
- Relative frontend API URLs.
- Frontend Docker health check.
- Docker Compose dependency on healthy backend.
- Frontend exposed on host port 3000.

## Run

docker compose up -d --build

Open:

http://localhost:3000

Backend:

http://localhost:8000/health

Frontend health:

http://localhost:3000/health

## Verification

- Frontend TypeScript/Vite production build.
- Deployment configuration checks.
- Docker Compose configuration validation.
- Frontend container build.
- Frontend HTTP health check.
- API reverse-proxy authentication route check.

## Security Notes

The included PostgreSQL password is a local development placeholder.
Use managed secrets and HTTPS/TLS before public production deployment.
Do not expose development credentials publicly.

## Limitations

Successful container deployment does not establish model accuracy,
production security certification, or public internet availability.
