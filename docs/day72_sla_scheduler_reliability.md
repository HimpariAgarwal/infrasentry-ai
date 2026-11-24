# Day 72 - SLA Scheduler Reliability

Added a reusable execution reliability decorator.

Features:
- Prevents overlapping executions within one Python process.
- Measures execution duration.
- Captures exceptions without leaving the lock held.
- Allows subsequent executions after a failure.

Important:
This lock is process-local. It does not coordinate multiple backend workers.
The helper is tested independently and is not yet wired into the live scheduler.
