from fastapi import Depends
from app.core.config import Settings, settings
from app.domain.interfaces import ListingProvider
from app.infrastructure.providers.mock_provider import MockListingProvider
from app.infrastructure.providers.real_provider import RealListingProvider
from app.infrastructure.providers.fallback_provider import FallbackListingProvider
from app.services.listing_service import ListingService


def get_settings() -> Settings:
    return settings


def get_listing_provider(settings: Settings = Depends(get_settings)) -> ListingProvider:
    if settings.AI_PROVIDER.lower() == "real":
        primary = RealListingProvider()
    else:
        primary = MockListingProvider()

    if settings.AI_FALLBACK_ENABLED:
        return FallbackListingProvider(primary=primary, fallback=MockListingProvider())
    return primary


def get_listing_service(
    provider: ListingProvider = Depends(get_listing_provider),
) -> ListingService:
    return ListingService(provider)
