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
all_match = True
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
    if verdict != "Збіг":
        all_match = False
    print(f"| {i} | {desc[:25]}... ({cond}) | {platform_label} | {expected} | {actual} | {ms:.0f} | {verdict} |")
    print(f"    -> Опис [{platform_label}]: {result.get('description')}")

# Additional checks for Lab Work No. 6 new functionality
print("\n=== Перевірка нового функціоналу (Lab Work 6) ===")

# 1. Luxury brand test
resp_luxury = client.post("/api/v1/listing", json={"description": "Куртка Gucci, нова", "condition": "new", "platform": "OLX", "brand_tier": "luxury"})
data_luxury = resp_luxury.json()
print(f"Luxury brand tier test: status={data_luxury.get('status')}, brand_tier={data_luxury.get('brand_tier')}, price_max={data_luxury.get('price_max')}")
assert data_luxury.get("brand_tier") == "luxury"
assert data_luxury.get("price_max") > 1000

# 2. Defect penalty test
resp_defect = client.post("/api/v1/listing", json={"description": "Куртка Zara, пляма та дірка на рукаві", "condition": "good", "platform": "OLX"})
data_defect = resp_defect.json()
print(f"Defect penalty test: price_min={data_defect.get('price_min')}, price_max={data_defect.get('price_max')}")
assert data_defect.get("price_max") < 500

# 3. Low confidence suggestions test
resp_low = client.post("/api/v1/listing", json={"description": "щось дивне і незрозуміле", "condition": "good", "platform": "OLX"})
data_low = resp_low.json()
print(f"Low confidence suggestions test: status={data_low.get('status')}, hint={data_low.get('hint')}, suggestions={data_low.get('suggestions')}")
assert data_low.get("status") == "low_confidence"
assert isinstance(data_low.get("suggestions"), list)
assert len(data_low.get("suggestions")) > 0

print("Всі додаткові перевірки пройдено успішно!")
if not all_match:
    raise AssertionError("Деякі базові сценарії не збіглися!")
