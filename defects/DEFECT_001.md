# DEFECT-001: OAuth2 Login Returns 422 in Swagger & Tests

## Environment
Local / CI

## Severity / Priority
Medium / High

## Description
Login endpoint returned 422 when called with JSON payload.

## Steps
1. Call POST /auth/login with JSON body
2. Observe 422 Unprocessable Entity

## Expected
200 OK with access token

## Actual
422 response

## Root Cause
OAuth2PasswordRequestForm requires form-encoded input, not JSON.

## Fix
Updated endpoint to accept OAuth2 form data and aligned tests & frontend.

## Regression Coverage
- backend/app/tests/test_auth_api.py
- security tests

## Status
Closed
