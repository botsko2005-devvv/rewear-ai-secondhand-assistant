from typing import Protocol
from app.domain.models import ListingCommand, ListingDraft


class ListingProvider(Protocol):
    async def generate(self, command: ListingCommand) -> ListingDraft:
        ...
