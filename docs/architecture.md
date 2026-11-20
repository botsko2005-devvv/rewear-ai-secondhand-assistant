# Архітектура системи

## Загальна схема взаємодії
Система побудована за клієнт-серверною архітектурою з розподілом відповідальності: мобільний застосунок відповідає за введення даних, первинну валідацію форми та відображення станів UI, а валідація контракту, бізнес-логіка й AI-обробка виконуються на backend.

```text
[Mobile: Android (Kotlin + Jetpack Compose)]
       │  HTTP POST /api/v1/listing (JSON)
       ▼
[Backend: FastAPI + Pydantic (Python)]
       │  provider.generate(description, condition, size)
       ▼
[AI Component: MockProvider (правила за ключовими словами)]
```

## Структура репозиторію
```text
rewear-ai-secondhand-assistant/
├── backend/
│   ├── main.py               # FastAPI-застосунок, маршрути /health і /api/v1/listing, обробка помилок
│   ├── models.py             # Pydantic-моделі запиту, відповіді та помилок
│   ├── ai_provider.py        # AI-компонент класифікації та рекомендації ціни
│   ├── test_ai.py            # Скрипт перевірки 6 тестових сценаріїв AI
│   ├── start.bat             # Скрипт швидкого запуску uvicorn на Windows
│   ├── requirements.txt      # Залежності Python (fastapi, uvicorn, python-dotenv)
│   └── .env.example          # Шаблон змінних середовища
├── mobile/
│   └── app/src/main/java/com/rewear/ai/
│       ├── MainActivity.kt     # Головний екран (ListingScreen) та картка результату (ResultCard)
│       ├── ListingViewModel.kt # Керування станами UiState та HTTP-викликами через корутини
│       ├── ApiService.kt       # Retrofit-інтерфейс та OkHttp-клієнт із таймаутами 10 с
│       └── ListingModels.kt  # DTO-моделі JSON, доменна модель Listing та sealed class UiState
├── docs/
│   ├── screenshots/          # Скріншоти тестування сценаріїв MVP
│   ├── project-overview.md   # Огляд проєкту та межі MVP
│   ├── requirements.md       # Статус вимог відносно ЛР1
│   ├── architecture.md       # Архітектура та структура репозиторію
│   ├── api-contract.md       # Специфікація REST API
│   ├── ai-component.md       # Опис логіки AI-компонента
│   ├── testing.md            # Результати інтеграційних та AI-тестів
│   ├── known-limitations.md  # Відомі обмеження поточної версії
│   ├── decisions.md          # Архітектурні та технічні рішення
│   └── ai-instructions.md    # Правила роботи для coding-агента
├── CLAUDE.md                 # Точка входу інструкцій для Claude Code
├── .gitignore
└── README.md
```

## Стани мобільного інтерфейсу (`UiState`)
`ListingViewModel` керує станом екрана через `sealed class UiState`:
1. `Idle` — початковий стан до натискання кнопки генерації.
2. `Loading` — активний HTTP-запит (відображається `CircularProgressIndicator`, кнопка блокується).
3. `Success(listing)` — отримано успішну відповідь (`status == "ok"`), відображається картка з категорією, ціною, заголовком, описом і кнопкою копіювання.
4. `NoResult(hint)` — отримано `status == "low_confidence"`, відображається порада уточнити опис.
5. `Error(message)` — помилка валідації, мережі, таймауту або парсингу JSON із кнопкою «Повторити».

## Локальне мережеве підключення
Backend запускається на `0.0.0.0:8000`. Для з'єднання емулятора Android із локальним сервером використовується прокидання порту `adb reverse tcp:8000 tcp:8000` та `BASE_URL = "http://127.0.0.1:8000/"`.