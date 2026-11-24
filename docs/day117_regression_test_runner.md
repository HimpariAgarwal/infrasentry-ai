# Day 117 - Automated Regression Test Runner

## Objective
Provide one command to discover and execute the project's Python
unittest test suite.

## Features
- Automatic test discovery
- Standard unittest execution
- Failure and error summaries
- Skipped test reporting
- Configurable test directory
- Machine-readable exit status

## Run

```powershell
python scripts/regression_test_runner.py
```

Quiet mode:

```powershell
python scripts/regression_test_runner.py --quiet
```

Custom test directory:

```powershell
python scripts/regression_test_runner.py --test-dir tests
```

## Exit codes
- 0: All discovered tests passed.
- 1: One or more tests failed.
- 2: Runner configuration or discovery error.

## Limitations
This runner executes Python unittest tests only.
It does not automatically run frontend tests, browser tests,
Docker builds, or external integration tests.
