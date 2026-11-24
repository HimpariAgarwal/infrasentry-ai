# Day 116 - API Contract Validation

## Objective
Validate the FastAPI OpenAPI specification automatically.

## Validations
- OpenAPI 3.x version
- API metadata and title
- Non-empty API paths
- Valid path definitions
- HTTP operation definitions
- Response definitions
- Duplicate operation IDs

## Run

```powershell
python scripts/api_contract_validator.py
```

Custom URL:

```powershell
python scripts/api_contract_validator.py --url http://localhost:8000/openapi.json
```

## Unit tests

```powershell
python -m unittest discover -s tests -p "test_api_contract_validator.py" -v
```

## Exit codes
- 0: Contract validation passed.
- 1: Contract contains validation issues.
- 2: Specification could not be fetched or parsed.

## Limitations
This validates structural OpenAPI metadata. It does not execute
API requests, validate business logic, or prove response schemas
match runtime responses.
