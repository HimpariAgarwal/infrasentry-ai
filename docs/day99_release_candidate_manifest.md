# Day 99 - Release Candidate Manifest

## Objective
Generate a SHA-256 integrity manifest for Git-tracked project files.

## Features
- SHA-256 file hashes.
- Git commit and branch metadata.
- Required project file checks.
- Runtime and sensitive file exclusions.
- Atomic JSON output.

## Run

`python backend/release_candidate_manifest.py`

## Output

`backend/logs/release_candidate_manifest.json`

The generated manifest is runtime data and is not committed.

## Excluded
- `.env` files
- logs and runtime data
- datasets
- model weights
- backups
- virtual environments
- node_modules
- Python bytecode

## Tests

`python -m unittest backend.test_release_candidate_manifest -v`

## Limitations
The manifest hashes Git-tracked files only. It does not prove
that a release is secure, malware-free, or functionally correct.
It is an integrity snapshot, not a digital signature.
