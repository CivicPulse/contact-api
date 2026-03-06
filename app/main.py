from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    yield


def create_app() -> FastAPI:
    from app.api.v1.contacts import router as contacts_router

    application = FastAPI(title="Contact API", lifespan=lifespan)

    application.include_router(contacts_router, prefix="/api/v1")

    @application.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return application


app = create_app()
