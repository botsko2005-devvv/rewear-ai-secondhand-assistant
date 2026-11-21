# Архітектура системи

## Загальна схема взаємодії
Система побудована за клієнт-серверною архітектурою з розподілом відповідальності: мобільний застосунок відповідає за введення даних, первинну валідацію форми, відображення станів UI та локальне збереження історії, а валідація контракту, бізнес-логіка й AI-обробка виконуються на backend.

```text
[Mobile: Android (Kotlin + Jetpack Compose + Room Database)]
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
│       ├── MainActivity.kt     # Головний екран (MainScreen, ListingScreen, HistoryScreen) та діалоги
│       ├── ListingViewModel.kt # Керування станами UiState, викликами API та доступом до HistoryRepository
│       ├── ApiService.kt       # Retrofit-інтерфейс та OkHttp-клієнт із таймаутами 10 с
│       ├── ListingModels.kt    # DTO-моделі JSON, доменна модель Listing та sealed class UiState
│       └── data/               # Шар локальних даних (Room Database)
│           ├── HistoryEntity.kt    # SQLite-таблиця listing_history
│           ├── HistoryDao.kt       # DAO-інтерфейс запитів до бази
│           ├── AppDatabase.kt      # Singleton RoomDatabase
│           └── HistoryRepository.kt# Обгортка над DAO для ViewModel
├── docs/
│   ├── screenshots/          # Скріншоти тестування сценаріїв MVP та ЛР4
│   ├── project-overview.md   # Огляд проєкту та межі MVP
│   ├── requirements.md       # Статус вимог відносно ЛР1 та ЛР4
│   ├── architecture.md       # Архітектура та структура репозиторію
│   ├── api-contract.md       # Специфікація REST API
│   ├── ai-component.md       # Опис логіки AI-компонента
│   ├── testing.md            # Результати інтеграційних та AI-тестів (включно з ЛР4)
│   ├── known-limitations.md  # Відомі обмеження поточної версії
│   ├── decisions.md          # Архітектурні та технічні рішення
│   └── ai-instructions.md    # Правила роботи для coding-агента
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

## Шар локального збереження (Room Database)
Для реалізації локальної історії (ЛР4) використано **Room Database** (версія 2.7.1) та кодогенерацію **KSP** (`2.2.10-2.0.2`):
- **`HistoryEntity`**: таблиця `listing_history` містить унікальний `id` (autoGenerate), `createdAt` (формат "yyyy-MM-dd HH:mm"), `timestamp`, `status` ("готово"), вхідні параметри (`description`, `condition`, `size`, `platform`) та результати AI-генерації (`category`, `title`, `resultDescription`, `priceMin`, `priceMax`, `currency`, `confidence`).
- **`HistoryDao`**: надає асинхронні методи (`suspend`) та реактивний потік `Flow<List<HistoryEntity>>` з сортуванням за `timestamp DESC`.
- **`AppDatabase`**: абстрактний клас `RoomDatabase` із singleton-ініціалізацією (`rewear_database`).
- **`HistoryRepository`**: інкапсулює роботу з DAO для `ListingViewModel`.

**Правило збереження в історію:** Запис зберігається в базу даних **ТІЛЬКИ** за умови успішної відповіді сервера (`response.isSuccessful`) та статусу `body.status == "ok"`. Помилки мережі, винятки, сервери з помилками та відповіді зі статусом `low_confidence` свідомо не зберігаються в історії.

## Локальне мережеве підключення
Backend запускається на `0.0.0.0:8000`. Для з'єднання емулятора Android із локальним сервером використовується прокидання порту `adb reverse tcp:8000 tcp:8000` та `BASE_URL = "http://127.0.0.1:8000/"`.
