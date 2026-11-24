# Day 87 - SLA Retry Profiles Dashboard

## Features
- Displays Fast, Standard and Conservative retry profiles.
- Fetches profile data from the backend API.
- Shows maximum attempts, initial delay and backoff factor.
- Includes loading, error, empty and refresh states.
- Uses authenticated API requests.

## Integration
The component is intentionally not added to App.tsx in this day.
This keeps the new dashboard isolated until its build and API contract are verified.

## Verification
Run:
python backend/test_sla_retry_profiles_dashboard.py

Then:
cd frontend
npm run build
