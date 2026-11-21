import logging
import uuid
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from app.api.error_handlers import register_error_handlers
from app.api.routes.listing import router as listing_router

load_dotenv()
logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    app = FastAPI(title="ReWear AI API", version="0.1.0")

    @app.middleware("http")
    async def add_request_id_and_log(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logging.info(
            f"method={request.method} path={request.url.path} status_code={response.status_code} request_id={request_id}"
        )
        return response

    register_error_handlers(app)
    app.include_router(listing_router)
    return app


app = create_app()
