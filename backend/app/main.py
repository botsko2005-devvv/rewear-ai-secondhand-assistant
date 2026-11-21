import logging
from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.error_handlers import register_error_handlers
from app.api.routes.listing import router as listing_router

load_dotenv()
logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    app = FastAPI(title="ReWear AI API", version="0.1.0")
    register_error_handlers(app)
    app.include_router(listing_router)
    return app


app = create_app()
