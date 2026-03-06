from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    yield


def create_app() -> FastAPI:
    from app.api.v1.contacts import router as contacts_router

    application = FastAPI(title="Contact API", lifespan=lifespan)

    application.add_middleware(
        CORSMiddleware,
        allow_origin_regex=(
            r"https?://([\w-]+\.)?(civpulse\.org|votehatcher\.com|kerryhatcher\.com)$"
            r"|https?://localhost(:\d+)?$"
        ),
        allow_methods=["POST", "GET", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    application.include_router(contacts_router, prefix="/api/v1")

    @application.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return application


app = create_app()
