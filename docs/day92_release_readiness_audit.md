# Day 92 - Release Readiness Audit

## Objective
Create a lightweight repository release-readiness checker.

## Checks
- Required backend and frontend entry files.
- Git-tracked environment files.
- Git-tracked model weights.
- Git-tracked datasets.
- Git-tracked runtime logs.
- Git-tracked node_modules directories.

## Run the audit

`python backend/release_readiness_audit.py`

## Run automated tests

`python -m unittest backend.test_release_readiness_audit -v`

## Important
The audit only detects sensitive file paths in Git tracking.
It does not inspect file contents or guarantee that secrets are absent.

The audit does not delete or modify any files.
