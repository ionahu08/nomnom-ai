import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import router as auth_router
from src.api.food_logs import router as food_logs_router
from src.api.photos import router as photos_router
from src.api.profile import router as profile_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("NomNom backend starting up")
    yield
    logger.info("NomNom backend shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="NomNom Backend",
        description="API server for NomNom — AI-powered food tracker with a roasting cat",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(food_logs_router)
    app.include_router(photos_router)
    app.include_router(profile_router)

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
