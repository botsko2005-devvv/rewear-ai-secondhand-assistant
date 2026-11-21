import json
import httpx
from typing import Optional
from app.core.config import settings
from app.domain.models import ListingCommand, ListingDraft
from app.domain.errors import (
    AiProviderDomainError,
    AiTimeoutDomainError,
    InvalidAiResponseDomainError,
)


class RealListingProvider:
    """Реальний AI-провайдер для зовнішнього LLM API (напр. OpenAI Chat Completions) через httpx.AsyncClient."""

    async def generate(self, command: ListingCommand) -> ListingDraft:
        if not settings.AI_API_KEY:
            raise AiProviderDomainError("AI_API_KEY is not configured in environment settings.")

        cond = command.condition.value if hasattr(command.condition, "value") else command.condition
        plat = command.platform.value if hasattr(command.platform, "value") else (command.platform or "OLX")

        prompt = (
            f"Analyze the following secondhand clothing item description and generate a listing draft in JSON format.\n"
            f"Description: {command.description}\n"
            f"Condition: {cond}\n"
            f"Size: {command.size or 'N/A'}\n"
            f"Platform: {plat}\n"
            f"Return JSON with keys: status ('ok' or 'low_confidence'), category (string or null), "
            f"condition (string), price_min (int or null), price_max (int or null), currency ('UAH'), "
            f"title (string or null), description (string or null), hint (string or null), confidence (float)."
        )

        headers = {
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.AI_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful secondhand clothing listing assistant. Respond strictly in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SEC) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise AiTimeoutDomainError("AI request timed out") from exc
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            raise AiProviderDomainError(f"AI provider network or HTTP error: {exc}") from exc
        except Exception as exc:
            raise AiProviderDomainError(f"Unexpected AI provider error: {exc}") from exc

        try:
            content_str = data["choices"][0]["message"]["content"]
            parsed = json.loads(content_str)
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise InvalidAiResponseDomainError("Invalid JSON structure received from AI provider") from exc

        return ListingDraft(
            status=parsed.get("status", "ok"),
            category=parsed.get("category"),
            condition=parsed.get("condition", cond),
            price_min=parsed.get("price_min"),
            price_max=parsed.get("price_max"),
            currency=parsed.get("currency", "UAH"),
            title=parsed.get("title"),
            description=parsed.get("description"),
            hint=parsed.get("hint"),
            confidence=float(parsed.get("confidence", 0.8)),
        )
