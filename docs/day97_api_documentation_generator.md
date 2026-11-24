# Day 97 - API Documentation Generator

## Objective
Generate a Markdown API reference from the Day 95 and Day 96
static route inventory.

## Features
- Endpoint and HTTP method listing.
- Function and source-file information.
- HTTP method distribution.
- Duplicate route candidate reporting.
- Python parsing error reporting.
- Atomic documentation file replacement.

## Generate

`python backend/api_documentation_generator.py`

## Output

`docs/generated_api_reference.md`

The generated API reference is committed as a version-controlled
project documentation artifact.

## Tests

`python -m unittest backend.test_api_documentation_generator -v`

## Limitations
The generator does not resolve APIRouter prefixes, infer security
requirements, or discover dynamically registered routes.
