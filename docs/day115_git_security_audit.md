# Day 115 - Git Security Audit

## Objective
Prevent accidental tracking of common sensitive files in Git.

## Checks
- .env files
- Private key files
- Credential and secret JSON files
- Backup directories
- Virtual environment and dependency directories

## Run

From the repository root:

```powershell
python scripts/git_security_audit.py
```

For a custom repository:

```powershell
python scripts/git_security_audit.py --root .
```

## Tests

```powershell
python -m unittest discover -s tests -p "test_git_security_audit.py" -v
```

## Exit codes
- 0: No known sensitive filenames detected.
- 1: Sensitive tracked paths detected.
- 2: Audit could not run.

## Security limitations
This audit checks tracked filenames and paths only.
It does not inspect file contents, detect secrets embedded in source code,
or replace a dedicated secret-scanning tool.
Review findings before removing or changing tracked files.
