from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.router import api_router
from src.db.config import database, redis
from src.utils.schema import CustomException


def get_app() -> FastAPI:
    app = FastAPI(title="My Application", version="1.0.0", lifespan=lifespan)

    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure allowed origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    app.include_router(api_router)

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio

    if not database.is_connected:
        for attempt in range(5):
            try:
                await database.connect()
                break
            except Exception as e:
                if attempt < 4:
                    await asyncio.sleep(5)
                else:
                    raise e

    # Ensure Redis connection
    try:
        redis.ping()
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Redis: {e}") from e

    yield

    await database.disconnect()
    redis.close()
