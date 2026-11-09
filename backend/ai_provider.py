from typing import Optional


class AIError(Exception):
    """Помилка AI-компонента."""


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


class MockProvider:
    """Простий AI на правилах: визначає категорію, ціну, заголовок і опис."""

    def generate(self, description: str, condition, size: Optional[str]) -> dict:
        text = description.lower()

        # Тестові "гачки" для перевірки помилок (потрібні для тестових сценаріїв)
        if "__ai_error__" in text:
            raise AIError("simulated ai failure")
        if "__timeout__" in text:
            raise TimeoutError("simulated timeout")

        cond = condition.value if hasattr(condition, "value") else condition

        category: Optional[str] = None
        base_price = 0
        for name, (keywords, price) in CATEGORIES.items():
            if any(k in text for k in keywords):
                category, base_price = name, price
                break

        if category is None:
            return {
                "category": None,
                "price_min": None,
                "price_max": None,
                "title": None,
                "description": None,
                "confidence": 0.3,
            }

        price = base_price * CONDITION_FACTOR[cond]
        price_min = int(round(price * 0.85 / 10) * 10)
        price_max = int(round(price * 1.15 / 10) * 10)

        first_part = description.split(",")[0].strip()
        title = first_part[:1].upper() + first_part[1:]
        if size and "розмір" not in text:
            title += f", розмір {size}"

        ad_text = (
            f"{description.strip().rstrip('.')}. "
            f"Стан: {CONDITION_LABEL[cond]}. "
            f"Категорія: {category}. "
            f"Орієнтовна ціна: {price_min}–{price_max} грн."
        )

        confidence = 0.9 if len(description) > 30 else 0.7
        return {
            "category": category,
            "price_min": price_min,
            "price_max": price_max,
            "title": title,
            "description": ad_text,
            "confidence": confidence,
        }