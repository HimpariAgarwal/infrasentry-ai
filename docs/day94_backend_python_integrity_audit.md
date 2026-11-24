# Day 94 - Backend Python Integrity Audit

## Objective
Add a static syntax audit for backend Python source files.

## Features
- Recursively discovers Python files.
- Parses source using Python AST.
- Reports syntax errors with file and line information.
- Ignores virtual environments, backups, logs and cache folders.
- Does not modify project source files.

## Run audit

`python backend/python_integrity_audit.py`

## Run tests

`python -m unittest backend.test_python_integrity_audit -v`

## Limitations
This checks Python syntax only.
It does not prove runtime correctness, API behavior,
dependency availability or database connectivity.
