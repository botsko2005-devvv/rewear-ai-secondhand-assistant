from typing import Optional
from app.domain.models import ListingCommand, ListingDraft, Condition, Platform
from app.domain.errors import AiTimeoutDomainError, AiProviderDomainError

CATEGORIES = {
    "Куртки та верхній одяг": (["куртк", "пуховик", "вітровк", "пальто"], 800),
    "Взуття": (["кросівк", "черевик", "туфл", "кеди", "чобот"], 700),
    "Джинси та штани": (["джинс", "штани", "брюки"], 500),
    "Футболки та светри": (["футболк", "светр", "худі", "кофт", "толстовк"], 300),
    "Сукні та спідниці": (["сукн", "плаття", "спідниц"], 450),
    "Аксесуари": (["сумк", "рюкзак", "ремінь", "шапк", "шарф", "годинник"], 350),
}

CONDITION_FACTOR = {"new": 1.0, "excellent": 0.8, "good": 0.6, "fair": 0.4}
CONDITION_LABEL = {
    "new": "новий",
    "excellent": "відмінний",
    "good": "добрий",
    "fair": "задовільний",
}


class MockListingProvider:
    """Простий AI на правилах: визначає категорію, ціну, заголовок і опис (асинхронний)."""

    async def generate(self, command: ListingCommand) -> ListingDraft:
        text = command.description.lower()

        # Тестові "гачки" для перевірки помилок
        if "__ai_error__" in text:
            raise AiProviderDomainError("simulated ai failure")
        if "__timeout__" in text:
            raise AiTimeoutDomainError("simulated timeout")

        cond = command.condition.value if hasattr(command.condition, "value") else command.condition
        plat = command.platform.value if hasattr(command.platform, "value") else (command.platform or "OLX")

        category: Optional[str] = None
        base_price = 0
        for name, (keywords, price) in CATEGORIES.items():
            if any(k in text for k in keywords):
                category, base_price = name, price
                break

        if category is None:
            return ListingDraft(
                status="low_confidence",
                category=None,
                condition=cond,
                price_min=None,
                price_max=None,
                currency="UAH",
                title=None,
                description=None,
                hint="Не вдалося визначити річ. Уточніть опис: вкажіть тип речі, бренд і стан.",
                confidence=0.3,
            )

        price = base_price * CONDITION_FACTOR.get(cond, 0.6)
        price_min = int(round(price * 0.85 / 10) * 10)
        price_max = int(round(price * 1.15 / 10) * 10)

        first_part = command.description.split(",")[0].strip()
        title = first_part[:1].upper() + first_part[1:]
        if command.size and "розмір" not in text:
            title += f", розмір {command.size}"

        if plat == "eBay":
            cond_text = {"new": "New", "excellent": "Excellent", "good": "Good", "fair": "Fair"}.get(cond, cond)
            ad_text = (
                f"{command.description.strip().rstrip('.')}. "
                f"Condition: {cond_text}. "
                f"Category: {category}. "
                f"Estimated Price: {price_min}–{price_max} UAH. "
                f"International shipping available. Fast dispatch."
            )
        elif plat == "Grailed":
            cond_text = {"new": "Brand New / 10/10", "excellent": "Lightly Used / 9/10", "good": "Used / 8/10", "fair": "Worn / 7/10"}.get(cond, cond)
            size_str = f" / Size {command.size}" if command.size else ""
            ad_text = (
                f"{command.description.strip().rstrip('.')}{size_str}. "
                f"Condition: {cond_text}. "
                f"Category: {category}. "
                f"Price: {price_min}–{price_max} UAH. "
                f"#streetwear #archive #grailed #secondhand"
            )
        else:  # OLX
            cond_text = CONDITION_LABEL.get(cond, cond)
            ad_text = (
                f"{command.description.strip().rstrip('.')}. "
                f"Стан: {cond_text}. "
                f"Категорія: {category}. "
                f"Орієнтовна ціна: {price_min}–{price_max} грн. "
                f"Безпечна доставка OLX або самовивіз."
            )

        confidence = 0.9 if len(command.description) > 30 else 0.7
        return ListingDraft(
            status="ok",
            category=category,
            condition=cond,
            price_min=price_min,
            price_max=price_max,
            currency="UAH",
            title=title,
            description=ad_text,
            hint=None,
            confidence=confidence,
        )
