# Day 47 - JWT Security Regression Tests

Automated tests for backend API access control.

## Test coverage

1. Missing bearer token returns HTTP 401.
2. Invalid JWT returns HTTP 401.
3. Valid JWT allows protected endpoint access.
4. Expired JWT returns HTTP 401.
5. Public health endpoint remains accessible.
6. Missing JWT secret returns HTTP 503.

## Run tests

python -m unittest backend.test_api_access_control

These tests use an isolated FastAPI test application and do not modify
production database records.
