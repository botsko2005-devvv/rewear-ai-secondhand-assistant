from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Condition(str, Enum):
    new = "new"
    excellent = "excellent"
    good = "good"
    fair = "fair"


class Platform(str, Enum):
    OLX = "OLX"
    eBay = "eBay"
    Grailed = "Grailed"


@dataclass
class ListingCommand:
    description: str
    condition: Condition | str
    size: Optional[str] = None
    platform: Optional[Platform | str] = Platform.OLX
    brand_tier: Optional[str] = None


@dataclass
class ListingDraft:
    status: str  # "ok" або "low_confidence"
    category: Optional[str] = None
    condition: Condition | str = Condition.good
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    currency: str = "UAH"
    title: Optional[str] = None
    description: Optional[str] = None
    hint: Optional[str] = None
    confidence: float = 0.0
    brand_tier: Optional[str] = None
    suggestions: Optional[list[str]] = None
