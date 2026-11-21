import logging
from app.domain.interfaces import ListingProvider
from app.domain.models import ListingCommand, ListingDraft
from app.domain.errors import AiProviderDomainError, AiTimeoutDomainError

logger = logging.getLogger("rewear")


class FallbackListingProvider:
    """Провайдер-обгортка для реалізації патерну Fallback (резервний AI-сервіс)."""

    def __init__(self, primary: ListingProvider, fallback: ListingProvider):
        self.primary = primary
        self.fallback = fallback

    async def generate(self, command: ListingCommand) -> ListingDraft:
        try:
            return await self.primary.generate(command)
        except (AiProviderDomainError, AiTimeoutDomainError) as exc:
            logger.warning(
                f"Primary AI provider failed ({type(exc).__name__}): {exc}. "
                f"Switching to fallback provider."
            )
            draft = await self.fallback.generate(command)
            fallback_note = "(Резервна оцінка: основний AI-сервіс тимчасово недоступний)"
            if draft.hint:
                draft.hint = f"{draft.hint} {fallback_note}"
            else:
                draft.hint = fallback_note
            return draft
