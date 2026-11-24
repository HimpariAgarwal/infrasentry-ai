# Day 96 - API Inventory JSON Reporting

## Objective
Export the static API route inventory into a structured JSON report.

## Report fields
- Schema version
- Python files scanned
- Total routes
- Files containing routes
- HTTP method distribution
- Route definitions
- Duplicate method/path candidates
- Python parsing errors

## Generate report

`python backend/api_route_inventory_report.py`

## Output

`backend/logs/api_route_inventory.json`

The generated report is runtime output and should not be committed.

## Run tests

`python -m unittest backend.test_api_route_inventory_report -v`

## Dependency
Uses the Day 95 `api_route_inventory.py` scanner.

## Limitations
This report reflects static route decorators.
It does not include dynamically registered routes or
automatically resolve APIRouter prefixes.
