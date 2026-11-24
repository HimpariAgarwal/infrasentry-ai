# Day 90 - SLA Retry Comparison Dashboard

## Overview
Added a frontend dashboard to compare configured SLA retry profiles.

## Data source
GET `/api/v1/sla/retry-comparison/`

## Displayed profiles
- Fast
- Standard
- Conservative

## Metrics
- Maximum attempts
- Initial delay
- Backoff factor
- Total accumulated waiting time

## UI behavior
- Authenticated API request
- Loading and error states
- Manual refresh
- Responsive profile cards

## Integration
The dashboard component is standalone in this task. It is not automatically
inserted into App.tsx; navigation integration is kept as a separate task.

## Verification
Run:

`python -m unittest backend.test_sla_retry_comparison_dashboard -v`

Then run `npm run build` inside the frontend folder.
