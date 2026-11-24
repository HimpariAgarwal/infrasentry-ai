# Day 86 - SLA Retry Profiles API

## Endpoints

### List all profiles
GET /api/v1/sla/retry-profiles

Returns fast, standard and conservative retry configurations.

### Read one profile
GET /api/v1/sla/retry-profiles/{profile_name}

Returns one configuration. Unknown profile names return HTTP 404.

## Integration
- Added a dedicated FastAPI router.
- Registered the router in backend/main.py.
- Existing retry engine and live scheduler behaviour remain unchanged.

## Verification
Run:
python backend/test_sla_scheduler_retry_profiles_api.py
python backend/test_sla_scheduler_retry_profiles_integration.py
