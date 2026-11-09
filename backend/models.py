from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Condition(str, Enum):
    new = "new"
    excellent = "excellent"
    good = "good"
    fair = "fair"


class ListingRequest(BaseModel):
    description: str = Field(..., max_length=500)
    condition: Condition
    size: Optional[str] = Field(None, max_length=10)

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Опис не може бути порожнім")
        return v


class ListingResponse(BaseModel):
    status: str  # "ok" або "low_confidence"
    category: Optional[str] = None
    condition: Condition
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    currency: str = "UAH"
    title: Optional[str] = None
    description: Optional[str] = None
    hint: Optional[str] = None
    confidence: float


class ErrorResponse(BaseModel):
    error: str
    message: str