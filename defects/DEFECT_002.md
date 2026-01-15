# DEFECT-002: bcrypt/passlib incompatibility causing startup failure

## Severity
High

## Description
FastAPI failed at startup when hashing passwords.

## Root Cause
bcrypt version incompatible with passlib.

## Fix
Pinned bcrypt==4.0.1

## Regression
- Startup verified
- Auth tests pass

## Status
Closed