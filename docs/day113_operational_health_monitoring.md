# Day 113 - Operational Health Monitoring

## Objective
Provide a lightweight production health monitor for InfraSentry AI.

## Components
- Frontend health endpoint
- Backend health endpoint
- HTTP status validation
- Connection failure handling
- Configurable request timeout
- Overall HEALTHY or DEGRADED result
- Non-zero exit code when a service is unhealthy

## Run

From the project root:

```powershell
python scripts/production_health_check.py
```

Custom endpoints:

```powershell
python scripts/production_health_check.py --frontend http://localhost:3000/health --backend http://localhost:8000/health
```

Custom timeout:

```powershell
python scripts/production_health_check.py --timeout 10
```

## Exit codes
- 0: All monitored endpoints returned HTTP 200.
- 1: At least one endpoint was unhealthy.

## Tests

```powershell
python -m unittest discover -s tests -p "test_production_health_check.py" -v
```

## Scope and limitations
This is an HTTP availability check, not a deep database, model-accuracy,
or infrastructure performance assessment. It does not automatically
restart services or send alerts.
