import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.domain.errors import (
    AiTimeoutDomainError,
    AiProviderDomainError,
    InvalidAiResponseDomainError,
)
from app.services.listing_service import ForbiddenItemDomainError

logger = logging.getLogger("rewear")


def error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": code, "message": message})


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        return error_response(
            422,
            "validation_error",
            "Некоректні дані: опис має містити 1–500 символів, стан — одне зі значень "
            "new, excellent, good, fair.",
        )

    @app.exception_handler(AiTimeoutDomainError)
    async def ai_timeout_handler(request: Request, exc: AiTimeoutDomainError):
        logger.warning(f"AI timeout: {exc.message}")
        return error_response(504, "ai_timeout", "AI не відповів вчасно. Спробуйте ще раз.")

    @app.exception_handler(AiProviderDomainError)
    async def ai_provider_handler(request: Request, exc: AiProviderDomainError):
        logger.warning(f"AI error: {exc.message}")
        return error_response(502, "ai_error", "Помилка AI-сервісу. Спробуйте пізніше.")

    @app.exception_handler(InvalidAiResponseDomainError)
    async def invalid_ai_response_handler(request: Request, exc: InvalidAiResponseDomainError):
        logger.warning(f"Invalid AI response: {exc.message}")
        return error_response(502, "ai_error", "Помилка AI-сервісу. Спробуйте пізніше.")

    @app.exception_handler(ForbiddenItemDomainError)
    async def forbidden_item_handler(request: Request, exc: ForbiddenItemDomainError):
        return error_response(422, "forbidden_item", exc.message)

    @app.exception_handler(Exception)
    async def unexpected_handler(request: Request, exc: Exception):
        logger.exception("Unexpected error")
        return error_response(502, "ai_error", "Внутрішня помилка. Спробуйте пізніше.")
