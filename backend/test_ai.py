import json
import time
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

CASES = [
    ("Куртка Zara, розмір M, носив один сезон, дрібна потертість на рукаві", "good", "OLX", "Куртки та верхній одяг"),
    ("Кросівки Nike Air Max, майже нові, розмір 42", "excellent", "eBay", "Взуття"),
    ("Джинси Levi's 501, потерті на колінах", "fair", "Grailed", "Джинси та штани"),
    ("Сукня літня квіткова, одягала двічі", "excellent", "OLX", "Сукні та спідниці"),
    ("Сумка шкіряна чорна, зовсім нова", "new", "eBay", "Аксесуари"),
    ("щось дивне і незрозуміле", "good", "OLX", "low_confidence"),
    # Зворотна сумісність: запит без поля platform (має дефолтно працювати як OLX)
    ("Худі чорне oversize, нове", "new", None, "Футболки та светри"),
]


print("| № | Вхідні дані | Платформа | Очікувано | Фактично | Час, мс | Висновок |")
print("|---|---|---|---|---|---|---|")
for i, (desc, cond, plat, expected) in enumerate(CASES, 1):
    payload = {"description": desc, "condition": cond}
    if plat is not None:
        payload["platform"] = plat
    
    start = time.perf_counter()
    response = client.post("/api/v1/listing", json=payload)
    ms = (time.perf_counter() - start) * 1000
    
    result = response.json()
    actual = result["category"] if result["status"] == "ok" else "low_confidence"
    platform_label = plat if plat else "default (OLX)"
    verdict = "Збіг" if actual == expected else "Розбіжність"
    print(f"| {i} | {desc[:25]}... ({cond}) | {platform_label} | {expected} | {actual} | {ms:.0f} | {verdict} |")
    print(f"    -> Опис [{platform_label}]: {result.get('description')}")
