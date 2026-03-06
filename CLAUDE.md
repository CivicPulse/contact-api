# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Lint
uv run ruff check .
uv run ruff check --fix .

# Run tests
uv run pytest
uv run pytest tests/path/to/test_file.py::test_name  # single test

# Database migrations
uv run python main.py db upgrade      # apply all pending migrations
uv run python main.py db downgrade    # roll back one migration
uv run python main.py db current      # show current revision

# Start dev server
uv run python main.py serve
```

## Architecture

The entrypoint is `main.py` — a **Typer CLI** with two commands: `serve` (launches uvicorn) and a `db` subgroup (wraps alembic). The FastAPI app itself lives in `app/main.py` as a factory function `create_app()`.

**Request flow:** `app/api/v1/contacts.py` → `app/db/session.py` (async SQLAlchemy session via `get_db()` dependency) → `app/db/models.py` (`ContactSubmission`).

**Config** is loaded at import time from `app/core/config.py` via `pydantic-settings`. `DATABASE_URL` is required — copy `.env.example` to `.env` before running locally. The `DATABASE_URL` must use the `postgresql+asyncpg://` scheme for the app; alembic's `env.py` automatically swaps it to `postgresql://` for the synchronous migration runner.

**Logging** (`app/core/logging.py`) removes loguru's default handler and installs a stderr handler, then intercepts the stdlib `logging` module so uvicorn and SQLAlchemy logs flow through loguru.

## Key Constraints

- `email-validator` (via `pydantic[email]`) is required for `EmailStr` — it is a declared dependency.
- `ContactCreate` enforces that at least one of `email` or `phone` is provided via a `model_validator`.
- The `POST /api/v1/contacts` endpoint reads `X-Forwarded-For` before falling back to `request.client.host` for accurate IP capture behind a k8s ingress.
- The alembic migration (`alembic/versions/0001_*.py`) runs `CREATE EXTENSION IF NOT EXISTS pgcrypto` to enable `gen_random_uuid()`.
- The k8s `secret.yaml` is a **template only** — never commit real values.
