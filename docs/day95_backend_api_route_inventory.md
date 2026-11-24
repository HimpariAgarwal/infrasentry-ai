# Day 95 - Backend API Route Inventory

## Objective
Build a static inventory of FastAPI-style HTTP route decorators.

## Features
- Detects GET, POST, PUT, PATCH, DELETE, OPTIONS and HEAD.
- Supports synchronous and asynchronous route functions.
- Records method, decorator path, function and source file.
- Reports duplicate method/path candidates.
- Ignores virtual environments, backups and cache directories.

## Run inventory

`python backend/api_route_inventory.py`

## Run tests

`python -m unittest backend.test_api_route_inventory -v`

## Limitations
This is a static decorator-level inventory.
It does not calculate effective paths from APIRouter prefixes.
It does not detect dynamically registered routes.
Duplicate candidates require manual review and are not automatically treated as errors.
