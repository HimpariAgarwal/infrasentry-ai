# Day 50 - Security Analytics and Threat Detection

## Features
- Analyzes security audit events from the last 24 hours.
- Counts events per IP address.
- Flags IP addresses with at least 5 events.
- Assigns medium or high risk based on event frequency.
- Provides total events, unique IPs, and risk level.

## API
GET /api/v1/security/threat-analysis

## Authentication
The endpoint is protected by the existing JWT API access-control middleware.

## Limitations
This is a basic log-based heuristic, not a firewall or a definitive attack detector.
Shared IPs, proxies, and legitimate repeated requests can cause false positives.
