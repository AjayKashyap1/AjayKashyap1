# QC Intel (Quick Commerce Intelligence)

Enterprise SaaS analytics platform for Blinkit sellers, built as a multi-tenant application from day one.

## Stack

- Backend: FastAPI, SQLAlchemy 2, PostgreSQL, Redis, Celery, Playwright
- Frontend: React, TypeScript, Tailwind CSS, React Router, React Query, Leaflet, Apache ECharts
- Desktop: Electron shell for secure local scanner operations

## Quick start

1. Copy `.env.example` to `.env` and update secrets.
2. Start infrastructure and services:

```bash
docker compose up --build
```

3. API: <http://localhost:8000/docs>
4. Web app: <http://localhost:5173>

## Architecture

The repository is organized as a deployable monorepo:

- `backend/app/domain`: SQLAlchemy domain models and enums.
- `backend/app/repositories`: repository pattern for persistence.
- `backend/app/services`: business orchestration, scanner, reporting, AI analytics.
- `backend/app/api`: versioned FastAPI routes with dependency injection.
- `backend/app/workers`: Celery queue tasks for background scans and scheduled jobs.
- `frontend/src`: routed React application with reusable components, hooks, API clients and pages.
- `desktop`: Electron wrapper for desktop distribution.

