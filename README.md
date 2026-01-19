# Quality Engineering Demo

## Overview
This repository is a **full-stack Quality Engineering (QE) demo application** designed to simulate and demonstrate **System Integration Testing (SIT), continuous testing, automation strategy, and defect management**.

The project showcases how a Quality Engineer enables quality across the **entire application lifecycle**, from UI to API to database, using **automation-first practices**.

This demo intentionally prioritizes **deterministic, synchronous processing** to ensure stable end-to-end testing and reliable CI execution.

---

## Goals of This Demo
- Demonstrate **full-stack testing ownership** (UI, API, DB)
- Implement **API, security, regression, and SIT automation**
- Show **defect management and root-cause analysis**
- Enable **continuous testing via GitHub Actions**
- Provide a **realistic QE Lead / Consultant workflow**

---


---

## Test Strategy

### Test Pyramid
- **API Tests (Primary)**  
  Auth, validation, negative paths, regression
- **Security Tests**  
  RBAC, unauthorized access, token handling
- **System Integration Tests (SIT)**  
  UI → API → DB → API → UI
- **UI Smoke Tests**  
  Critical user workflows only

### pytest Markers
- `smoke`
- `security`
- `sit`
- `regression`

Example:
```bash
pytest -m smoke
pytest -m security
pytest -m sit


python3.11 -m venv venv        
source venv/bin/activate