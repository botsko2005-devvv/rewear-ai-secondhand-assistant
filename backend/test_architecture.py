import os
import sys
import unittest
from unittest.mock import patch

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import settings
from app.domain.models import Condition, Platform, ListingCommand, ListingDraft
from app.domain.errors import (
    AiProviderDomainError,
    AiTimeoutDomainError,
    InvalidAiResponseDomainError,
)
from app.infrastructure.providers.mock_provider import MockListingProvider
from app.infrastructure.providers.real_provider import RealListingProvider
from app.infrastructure.providers.fallback_provider import FallbackListingProvider
from app.services.listing_service import ListingService
from app.api.dependencies import get_listing_provider


class TimeoutFakeProvider:
    async def generate(self, command: ListingCommand) -> ListingDraft:
        raise AiTimeoutDomainError("Simulated timeout")


class FailingFakeProvider:
    async def generate(self, command: ListingCommand) -> ListingDraft:
        raise AiProviderDomainError("Simulated provider failure")


class TestBackendArchitecture(unittest.IsolatedAsyncioTestCase):
    async def test_1_service_with_mock_provider_platforms(self):
        """1. Перевірка ListingService + MockListingProvider для OLX, eBay та Grailed без FastAPI."""
        service = ListingService(provider=MockListingProvider())

        olx_draft = await service.generate_listing(
            ListingCommand("Куртка Zara, розмір M", Condition.good, "M", Platform.OLX)
        )
        ebay_draft = await service.generate_listing(
            ListingCommand("Кросівки Nike Air Max", Condition.excellent, "42", Platform.eBay)
        )
        grailed_draft = await service.generate_listing(
            ListingCommand("Джинси Levi's 501", Condition.fair, "32", Platform.Grailed)
        )

        self.assertEqual(olx_draft.status, "ok")
        self.assertIn("Безпечна доставка OLX", olx_draft.description)
        self.assertIn("International shipping available", ebay_draft.description)
        self.assertIn("#grailed", grailed_draft.description)

    def test_2_di_override_timeout_returns_504(self):
        """2. Підміна провайдера через FastAPI Depends на TimeoutFakeProvider -> 504 ai_timeout."""
        app = create_app()
        app.dependency_overrides[get_listing_provider] = lambda: TimeoutFakeProvider()
        client = TestClient(app)

        resp = client.post(
            "/api/v1/listing",
            json={"description": "Куртка Zara, розмір M", "condition": "good", "platform": "OLX"},
        )
        self.assertEqual(resp.status_code, 504)
        self.assertEqual(resp.json()["error"], "ai_timeout")

    def test_3_di_override_provider_error_returns_502(self):
        """3. Підміна провайдера через FastAPI Depends на FailingFakeProvider -> 502 ai_error."""
        app = create_app()
        app.dependency_overrides[get_listing_provider] = lambda: FailingFakeProvider()
        client = TestClient(app)

        resp = client.post(
            "/api/v1/listing",
            json={"description": "Куртка Zara, розмір M", "condition": "good", "platform": "eBay"},
        )
        self.assertEqual(resp.status_code, 502)
        self.assertEqual(resp.json()["error"], "ai_error")

    async def test_4_real_provider_missing_key_and_invalid_json(self):
        """4. RealListingProvider без ключа та зі зламаним JSON кидає доменні помилки."""
        provider = RealListingProvider()
        cmd = ListingCommand("Куртка Zara", Condition.good, "M", Platform.OLX)
        original_key = settings.AI_API_KEY

        try:
            settings.AI_API_KEY = ""
            with self.assertRaises(AiProviderDomainError):
                await provider.generate(cmd)

            settings.AI_API_KEY = "test-fake-key"

            class FakeHttpResponse:
                def raise_for_status(self):
                    pass

                def json(self):
                    return {"choices": [{"message": {"content": "це не json {"}}]}

            class FakeAsyncClient:
                def __init__(self, *args, **kwargs):
                    pass

                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc, tb):
                    return False

                async def post(self, *args, **kwargs):
                    return FakeHttpResponse()

            with patch("httpx.AsyncClient", FakeAsyncClient):
                with self.assertRaises(InvalidAiResponseDomainError):
                    await provider.generate(cmd)
        finally:
            settings.AI_API_KEY = original_key

    async def test_5_fallback_provider_recovers_on_primary_failure(self):
        """5. Контрольне розширення FallbackListingProvider перемикається на резервний провайдер."""
        fallback_provider = FallbackListingProvider(
            primary=FailingFakeProvider(),
            fallback=MockListingProvider(),
        )
        service = ListingService(provider=fallback_provider)

        draft = await service.generate_listing(
            ListingCommand("Куртка Zara, розмір M", Condition.good, "M", Platform.OLX)
        )
        self.assertEqual(draft.status, "ok")
        self.assertEqual(draft.category, "Куртки та верхній одяг")
        self.assertIn("Резервна оцінка", draft.hint or "")

    def test_6_request_id_middleware_and_backward_compatibility(self):
        """6. Перевірка X-Request-ID, зворотної сумісності без platform та 422 при забороні."""
        app = create_app()
        client = TestClient(app)

        resp = client.post(
            "/api/v1/listing",
            headers={"X-Request-ID": "lab5-trace-001"},
            json={"description": "Худі чорне oversize", "condition": "new"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("X-Request-ID"), "lab5-trace-001")
        self.assertIn("Безпечна доставка OLX", resp.json()["description"])

        bad_resp = client.post(
            "/api/v1/listing",
            json={"description": "Продам пістолет", "condition": "good"},
        )
        self.assertEqual(bad_resp.status_code, 422)
        self.assertEqual(bad_resp.json()["error"], "forbidden_item")


if __name__ == "__main__":
    unittest.main(verbosity=2)
