from app.domain.interfaces import ListingProvider
from app.domain.models import ListingCommand, ListingDraft
from app.domain.errors import DomainError

BANNED_WORDS = ["зброя", "зброю", "пістолет", "наркотик"]


class ForbiddenItemDomainError(DomainError):
    """Помилка: заборонений товар до продажу."""
    def __init__(self, message: str = "Цей тип товарів заборонено до продажу."):
        super().__init__(message)


class ListingService:
    """Прикладний сервіс для бізнес-логіки генерації оголошень."""

    def __init__(self, provider: ListingProvider):
        self.provider = provider

    async def generate_listing(self, command: ListingCommand) -> ListingDraft:
        text = command.description.lower()
        if any(w in text for w in BANNED_WORDS):
            raise ForbiddenItemDomainError("Цей тип товарів заборонено до продажу.")

        if "__bad_json__" in text:
            from app.domain.errors import InvalidAiResponseDomainError
            raise InvalidAiResponseDomainError("це не json {")

        return await self.provider.generate(command)
