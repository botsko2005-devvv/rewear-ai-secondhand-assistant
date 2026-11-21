from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.domain.models import Condition, Platform, ListingCommand, ListingDraft


class ListingRequest(BaseModel):
    description: str = Field(..., max_length=500)
    condition: Condition
    size: Optional[str] = Field(None, max_length=10)
    platform: Optional[Platform] = Platform.OLX

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Опис не може бути порожнім")
        return v

    def to_command(self) -> ListingCommand:
        return ListingCommand(
            description=self.description,
            condition=self.condition,
            size=self.size,
            platform=self.platform or Platform.OLX,
        )


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

    @classmethod
    def from_draft(cls, draft: ListingDraft) -> "ListingResponse":
        return cls(
            status=draft.status,
            category=draft.category,
            condition=draft.condition,
            price_min=draft.price_min,
            price_max=draft.price_max,
            currency=draft.currency,
            title=draft.title,
            description=draft.description,
            hint=draft.hint,
            confidence=draft.confidence,
        )


class ErrorResponse(BaseModel):
    error: str
    message: str
