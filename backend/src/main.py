import uvicorn

from gunicorn_runner import GunicornApplication
from settings import settings


def main() -> None:
    if settings.reload:
        uvicorn.run(
            "src.application:get_app",
            host=settings.host,
            port=settings.port,
            reload=True,
        )
    else:
        GunicornApplication(
            "src.application:get_app",
            host=settings.host,
            port=settings.port,
            workers=settings.worker_count,
        ).run()


if __name__ == "__main__":
    main()
