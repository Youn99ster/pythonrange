# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
HackShop is an immersive web security education platform built around a realistic e-commerce workflow with intentionally designed vulnerabilities.

## Current Architecture
- Frontend: Jinja2 templates + Bootstrap 5 + JavaScript
- Backend: Flask (implemented)
- Database: MySQL (implemented)
- Cache: Redis (implemented)
- ORM/Migration: SQLAlchemy + Flask-Migrate
- Logging: app-level logging with console + rotating file handler

## Runtime and Deployment
- Entrypoint: `start.sh`
- WSGI: Gunicorn
- Dependency source: Dockerfile pip install list
- Container orchestration: Docker Compose (`web/mysql/redis`)
- Health checks enabled for MySQL, Redis, and Web service
- MySQL data persisted via named volume

## Data Initialization and Lab Reset
- `scripts/seed.py`: seed products/users/vouchers/mail/sample order
- `scripts/reset_lab.py`: reset DB/cache then reseed
- Optional boot flags:
  - `SEED_ON_BOOT=1`
  - `RESET_LAB_ON_BOOT=1`

## Key Commands (Docker Only)
### Start
```bash
docker compose down -v
docker compose up -d --build
```

### Inspect
```bash
docker compose ps
docker compose logs -f web
```

### In-container ops
```bash
docker compose exec web flask --app app routes
docker compose exec web flask --app app db upgrade
docker compose exec web python scripts/seed.py
docker compose exec web python scripts/reset_lab.py
```

## Vulnerability Scope (10)
- V-Auth-DoS
- V-Host-Inject
- V-CSRF-Pay
- V-Race-Condition
- V-IDOR-View
- V-IDOR-Modify
- V-SSRF
- V-SQL-Union
- V-SSTI
- V-Admin-AES

## Notes
- This repository intentionally includes vulnerable logic for education.
- Do not treat current behavior/configuration as a production security baseline.
- Use `docs/PRD.md` as the requirements baseline.
