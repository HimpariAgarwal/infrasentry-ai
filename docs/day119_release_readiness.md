# Day 119 - Production Release Readiness Gate

## Objective

Introduce a repeatable pre-release validation gate for InfraSentry AI.

## Implemented

- Required deployment and project file validation.
- Git tracked-file security inspection.
- Detection of tracked environment files, private keys,
  credential files and unintended backup directories.
- Docker Compose configuration validation.
- Optional Docker skip mode for isolated testing.
- Clear PASS / FAIL readiness report.
- Automated unit tests.

## Run

From the project root:

```powershell
python scripts/release_readiness_check.py
```

Skip Docker validation:

```powershell
python scripts/release_readiness_check.py --skip-docker
```

Run tests:

```powershell
python -m unittest discover -s tests -p "test_release_readiness_check.py" -v
```

## Release gate

A READY result means the configured checks passed.
It does not certify security, model accuracy or production infrastructure.
