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
- `ContactCreate` enforces that at least one of `email` or `phone` is provided via a `model_validator`. All string fields are sanitized (control chars stripped) by `field_validator`s in `app/schemas/contact.py`.
- The `POST /api/v1/contacts` endpoint reads `X-Forwarded-For` before falling back to `request.client.host` for accurate IP capture behind a k8s ingress.
- The alembic migration (`alembic/versions/0001_*.py`) runs `CREATE EXTENSION IF NOT EXISTS pgcrypto` to enable `gen_random_uuid()`.
- The k8s `secret.yaml` is a **template only** — never commit real values.
- CORS allows `*.civpulse.org`, `*.votehatcher.com`, `*.kerryhatcher.com`, and `localhost` (any port) via `allow_origin_regex` in `app/main.py`.

## Tests

There are currently no tests in this repo. The dev dependencies (`pytest`, `pytest-asyncio`, `httpx`) are declared but no test files exist yet. Use `httpx.AsyncClient` with `asgi_transport` to test the FastAPI app without a real database.

## GitOps / Deployment

Pushes to `main` trigger `.github/workflows/build-push.yaml`, which:
1. Builds and pushes the image to GHCR with tags `sha-<7-char-sha>` and `latest`
2. Runs a `deploy` job that patches both image lines in `k8s/deployment.yaml` with the pinned `sha-` tag and commits `[skip ci]` back to `main`
3. ArgoCD (namespace `argocd`) polls `k8s/` every ~3 minutes and auto-syncs to the cluster (`civpulse-dev` namespace)

ArgoCD UI is exposed at `/argocd` on the Tailscale node via Traefik (Tailscale only). `argocd/ingress.yaml` uses a `$TAILSCALE_HOST` placeholder — apply it with `envsubst`:

```bash
TAILSCALE_HOST=<your-node>.ts.net envsubst < argocd/ingress.yaml | kubectl apply -f -
```

Application manifest is `argocd/contact-api-app.yaml`; its IngressRoute is `argocd/ingress.yaml` (kept outside `k8s/` so ArgoCD doesn't manage itself).

**`[skip ci]` gotcha:** GitHub Actions skans the entire squash-merge commit message body for `[skip ci]`. If a PR description contains that text literally (e.g., describing the deploy job), the merge commit will skip CI. Rephrase or escape the text in PR bodies.
