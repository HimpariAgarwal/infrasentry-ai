# Day 48 - Security Audit Logging

## Recorded security events

- Missing bearer token
- Invalid JWT
- Expired JWT
- Invalid server JWT configuration

## Log location

backend/logs/security_audit.log

## Recorded fields

- UTC timestamp
- Event type
- Requested API path
- Client IP address
- Failure reason

## Security precautions

JWT tokens, passwords and authorization headers are never written
to the security audit log.

Runtime log files are excluded from Git.
