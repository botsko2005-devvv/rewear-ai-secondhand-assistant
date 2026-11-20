import json
import time
import urllib.request

URL = "http://127.0.0.1:8000/api/v1/listing"

CASES = [
    ("Куртка Zara, розмір M, носив один сезон, дрібна потертість на рукаві", "good", "Куртки та верхній одяг"),
    ("Кросівки Nike Air Max, майже нові, розмір 42", "excellent", "Взуття"),
    ("Джинси Levi's 501, потерті на колінах", "fair", "Джинси та штани"),
    ("Сукня літня квіткова, одягала двічі", "excellent", "Сукні та спідниці"),
    ("Сумка шкіряна чорна, зовсім нова", "new", "Аксесуари"),
    ("щось дивне і незрозуміле", "good", "low_confidence"),
]


def call(description: str, condition: str) -> dict:
    data = json.dumps({"description": description, "condition": condition}).encode()
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


print("| № | Вхідні дані | Очікувано | Фактично | Час, мс | Висновок |")
print("|---|---|---|---|---|---|")
for i, (desc, cond, expected) in enumerate(CASES, 1):
    start = time.perf_counter()
    result = call(desc, cond)
    ms = (time.perf_counter() - start) * 1000
    actual = result["category"] if result["status"] == "ok" else "low_confidence"
    price = f" ({result['price_min']}–{result['price_max']} грн)" if result["status"] == "ok" else ""
    verdict = "Збіг" if actual == expected else "Розбіжність"
    print(f"| {i} | {desc} ({cond}) | {expected} | {actual}{price} | {ms:.0f} | {verdict} |")