# Day 118 - GitHub Actions CI Pipeline

## Objective

Automate quality checks for InfraSentry AI whenever changes
are pushed to main or a pull request targets main.

## Workflow

File: .github/workflows/ci.yml

### Backend
- Python 3.11 setup
- Automated regression test runner

### Frontend
- Node.js 22 setup
- npm ci dependency installation
- ESLint validation
- Vite production build

### Deployment configuration
- Docker Compose configuration validation

## Security

- Repository permission is read-only.
- No credentials or environment secrets are required.
- No deployment or production infrastructure changes occur.

## Local validation

```powershell
python -m unittest discover -s tests -p "test_ci_workflow.py" -v
python scripts/regression_test_runner.py

cd frontend
npm ci
npm run lint
npm run build
cd ..

docker compose config -q
```

## Trigger

The workflow runs on:
- Push to main
- Pull requests targeting main

## Limitation

This workflow validates code quality and build configuration.
It does not deploy the application to a production server.
