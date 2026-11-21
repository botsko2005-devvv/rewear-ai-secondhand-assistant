from fastapi import APIRouter, Depends
from app.api.schemas import ListingRequest, ListingResponse
from app.api.dependencies import get_listing_service
from app.services.listing_service import ListingService

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/api/v1/listing", response_model=ListingResponse)
async def create_listing(
    req: ListingRequest,
    service: ListingService = Depends(get_listing_service),
) -> ListingResponse:
    command = req.to_command()
    draft = await service.generate_listing(command)
    return ListingResponse.from_draft(draft)
