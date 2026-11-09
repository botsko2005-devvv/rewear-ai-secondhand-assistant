import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ai_provider import AIError, MockProvider
from models import ListingRequest, ListingResponse

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rewear")

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
BANNED_WORDS = ["зброя", "зброю", "пістолет", "наркотик"]

app = FastAPI(title="ReWear AI API", version="0.1.0")
provider = MockProvider()


def error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": code, "message": message})


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return error(
        422,
        "validation_error",
        "Некоректні дані: опис має містити 1–500 символів, стан — одне зі значень "
        "new, excellent, good, fair.",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/listing", response_model=ListingResponse)
def create_listing(req: ListingRequest):
    text = req.description.lower()
    if any(w in text for w in BANNED_WORDS):
        return error(422, "forbidden_item", "Цей тип товарів заборонено до продажу.")

    try:
        result = provider.generate(req.description, req.condition, req.size)
    except TimeoutError:
        logger.warning("AI timeout")
        return error(504, "ai_timeout", "AI не відповів вчасно. Спробуйте ще раз.")
    except AIError:
        logger.warning("AI error")
        return error(502, "ai_error", "Помилка AI-сервісу. Спробуйте пізніше.")
    except Exception:
        logger.exception("Unexpected error")  # деталі лише в логах сервера
        return error(502, "ai_error", "Внутрішня помилка. Спробуйте пізніше.")

    if result["confidence"] < CONFIDENCE_THRESHOLD:
        return ListingResponse(
            status="low_confidence",
            condition=req.condition,
            confidence=result["confidence"],
            hint="Не вдалося визначити річ. Уточніть опис: вкажіть тип речі, бренд і стан.",
        )

    return ListingResponse(status="ok", condition=req.condition, **result)