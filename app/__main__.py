from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.__core__.application.logger import logger
from app.__core__.application.settings import get_settings
from app.infra.dependency import close_httpx_client
from app.infra.http.middleware.correlation_id import CorrelationIdMiddleware
from app.infra.http.router import auth, customers, favorites
from app.infra.postgres.database import close_db, init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("app_startup_complete")
    await init_db()

    yield

    await close_db()
    await close_httpx_client()
    logger.info("app_shutdown_complete")


def bootstrap() -> FastAPI:
    app = FastAPI(
        title="aiqfome Favorites API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url=None,
    )

    if settings.ENV == "prod":
        app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Authorization", "x-aiqfome-api-key"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=5)

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(customers.router, prefix="/customers", tags=["customers"])
    app.include_router(
        favorites.router,
        prefix="/customers/{customer_id}/favorites",
        tags=["favorites"],
    )

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = bootstrap()

if __name__ == "__main__":
    port = settings.API_PORT
    reload = settings.ENV == "dev"
    uvicorn.run(
        "app.__main__:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        access_log=True,
        workers=4,
    )
