# Day 102 - System Diagnostics Engine

## Objective
Create a lightweight diagnostics module for InfraSentry AI.

## Features
- Disk usage monitoring.
- Configurable disk warning threshold.
- Python runtime information.
- Platform information.
- Healthy and degraded status reporting.
- UTC timestamp.
- Diagnostic summary.

## Security
- Does not collect environment variables.
- Does not expose credentials or JWT secrets.
- Does not modify application configuration.
- Uses Python standard library only.

## Testing
Run:

python -m unittest backend/test_system_diagnostics.py -v

## Scope
This module is independently testable. API integration will be
handled separately after the diagnostics engine is validated.
