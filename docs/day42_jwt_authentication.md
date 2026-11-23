# Day 42 - JWT Authentication

## Features
- JWT access token generation
- OAuth2 password-based login
- Protected user profile endpoint
- Protected secure-check endpoint
- Invalid and expired token rejection

## API Endpoints
POST /api/v1/auth/token
GET  /api/v1/auth/me
GET  /api/v1/auth/secure-check

## Configuration
Set these environment variables before starting the backend:

JWT_SECRET_KEY = A unique random secret of at least 32 characters
ADMIN_USERNAME = Your administrator username
ADMIN_PASSWORD = A strong administrator password

Never commit credentials or secret keys to Git.

## Token
Algorithm: HS256
Expiration: 30 minutes
Token type: Bearer

## Important
The new authentication endpoints are protected.
Existing detection and history endpoints are not yet
enforced by JWT. Global authentication requires frontend
login integration and is a separate next step.
