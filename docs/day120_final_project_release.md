# InfraSentry AI - Final Project Release

## Project status

Day 120 - Final project completion milestone.

InfraSentry AI is a full-stack AI-assisted infrastructure
monitoring and incident-management project.

## Technology stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT authentication
- OpenAPI

### Frontend
- React
- TypeScript
- Vite
- Nginx

### AI and computer vision
- YOLO / Ultralytics integration
- Image-based detection workflow

### Deployment and engineering
- Docker
- Docker Compose
- GitHub Actions
- Automated regression tests
- Production health checks
- Git security audit
- Release readiness validation

## Engineering milestones

- Backend API and authentication
- Database integration
- AI detection workflow
- Incident and report management
- Analytics and dashboard
- Dockerized backend and database
- Nginx-based frontend deployment
- Operational monitoring scripts
- Git security audit
- API contract validation
- Automated regression runner
- GitHub Actions CI pipeline
- Production release readiness gate
- Final project completion checker

## Validation commands

```powershell
python scripts/regression_test_runner.py
python scripts/project_completion_check.py
python scripts/release_readiness_check.py
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
cd ..
```

Docker:

```powershell
docker compose config -q
docker compose ps
```

## Honest limitations

- Automated checks do not establish AI detection accuracy.
- Model performance requires a separately designed and labeled evaluation dataset.
- Local Docker configuration is not a production cloud deployment.
- Production credentials, HTTPS, backups, monitoring and infrastructure
  hardening must be configured for the target environment.
- CI passing does not replace security review or user acceptance testing.

## Portfolio description

InfraSentry AI - Full-Stack AI-Assisted Infrastructure Monitoring Platform

Developed a full-stack monitoring and incident-management platform
using React, TypeScript, FastAPI, PostgreSQL and Docker. Integrated
an AI-based image detection workflow, authenticated APIs, reporting,
analytics, operational health checks and GitHub Actions CI.

Repository:
https://github.com/HimpariAgarwal/infrasentry-ai
