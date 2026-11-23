# ReWear AI

Мобільний AI-помічник продавця секонд-хенду та вінтажного одягу для маркетплейсів **OLX, eBay, Grailed**.

## Ідея та призначення
Приватні продавці та реселери витрачають багато часу на підготовку оголошень: вибір категорії, оцінку вартості, написання заголовка й опису під формат конкретного майданчика. **ReWear AI** автоматизує цей процес: користувач вводить короткий опис речі, обирає стан, розмір та майданчик публікації (`OLX`, `eBay` або `Grailed`), а система визначає категорію, рекомендує діапазон ціни у гривнях (`UAH`) і формує готовий текст оголошення з можливістю копіювання в один клік. Усі успішно згенеровані оголошення зберігаються локально на пристрої у базі даних Room для перегляду історії, деталей та повторного копіювання.

## Технологічний стек

- **Mobile (`mobile/`):** Android, Kotlin, Jetpack Compose (Material 3), `AndroidViewModel`, Room Database (`2.7.1`) + KSP (`2.2.10-2.0.2`), Retrofit + Gson + OkHttp.
- **Backend (`backend/`):** Python 3.10+, FastAPI, Pydantic, Uvicorn, `httpx`, `python-dotenv` (шарувата архітектура з DI через `FastAPI Depends`).
- **AI-компонент (`backend/app/infrastructure/providers/`):** провайдери за контрактом `ListingProvider (Protocol)` — детермінований правиловий `MockListingProvider`, `RealListingProvider` та резервний `FallbackListingProvider`.

## Структура репозиторію та Knowledge Base
```text
rewear-ai-secondhand-assistant/
├── backend/                              # FastAPI сервер (шарувата архітектура ЛР5)
│   ├── main.py                           # Точка входу для uvicorn (реекспорт app)
│   ├── requirements.txt                  # Залежності Python
│   ├── test_ai.py                        # 7 регресійних сценаріїв генерації
│   ├── test_architecture.py              # 6 архітектурних автотестів ЛР5 (unittest)
│   └── app/
│       ├── main.py                       # Фабрика create_app() та X-Request-ID middleware
│       ├── core/
│       │   └── config.py                 # Централізовані налаштування Settings (.env)
│       ├── domain/
│       │   ├── models.py                 # Доменні моделі ListingCommand, ListingDraft
│       │   ├── errors.py                 # Доменні винятки DomainError
│       │   └── interfaces.py             # Інтерфейс ListingProvider (Protocol)
│       ├── infrastructure/providers/
│       │   ├── mock_provider.py          # Правиловий MockListingProvider
│       │   ├── real_provider.py          # Реальний LLM-провайдер (httpx.AsyncClient)
│       │   └── fallback_provider.py      # Резервний FallbackListingProvider
│       ├── services/
│       │   └── listing_service.py        # Прикладний сервіс ListingService
│       └── api/
│           ├── schemas.py                # Pydantic DTO (ListingRequest, ListingResponse)
│           ├── error_handlers.py         # Централізована обробка помилок (422/502/504)
│           ├── dependencies.py           # FastAPI Depends (composition root)
│           └── routes/
│               └── listing.py            # Тонкий роутер GET /health та POST /api/v1/listing
├── mobile/                               # Android-застосунок (Kotlin + Jetpack Compose)
│   └── app/src/main/java/com/rewear/ai/
│       ├── MainActivity.kt               # Головний екран, вкладки PrimaryTabRow, історія та діалоги
│       ├── ListingViewModel.kt           # ViewModel з інтеграцією HistoryRepository
│       ├── ApiService.kt                 # Retrofit-клієнт із таймаутами 10 с
│       ├── ListingModels.kt              # DTO-моделі JSON, доменна модель Listing та UiState
│       └── data/                         # Локальний шар даних (Room Database, ЛР4)
│           ├── HistoryEntity.kt          # SQLite-таблиця listing_history
│           ├── HistoryDao.kt             # DAO-інтерфейс запитів до бази
│           ├── AppDatabase.kt            # Singleton RoomDatabase
│           └── HistoryRepository.kt      # Обгортка над DAO для ViewModel
├── docs/                                 # Knowledge Base проєкту та скріншоти тестування
│   ├── project-overview.md               # Огляд проєкту, сценарій та межі MVP
│   ├── requirements.md                   # Статус функціональних і нефункціональних вимог
│   ├── architecture.md                   # Клієнт-серверна архітектура, стани UI та Room-шар
│   ├── api-contract.md                   # Специфікація REST API та формат помилок
│   ├── ai-component.md                   # Логіка AI-класифікації та ціноутворення
│   ├── testing.md                        # Інтеграційні, AI та архітектурні тести
│   ├── known-limitations.md              # Відомі обмеження поточної версії
│   ├── decisions.md                      # Архітектурні рішення та виправлені дефекти
│   ├── ai-instructions.md                # Правила роботи для AI-асистента (coding-агента)
│   └── screenshots/                      # Скріншоти екранів застосунку та роботи агента
├── GEMINI.md                             # Точка входу правил для Gemini CLI
├── .gitignore
└── README.md
```

## Інструкція із запуску

### 1. Запуск Backend (FastAPI)
```bash
cd backend
python -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- Перевірка стану сервісу: `http://127.0.0.1:8000/health` → `{"status":"ok"}`
- Інтерактивна документація Swagger UI: `http://127.0.0.1:8000/docs`
- Запуск автотестів AI-компонента: `python test_ai.py`
- Запуск архітектурних тестів ЛР5 (без зовнішнього API): `python test_architecture.py`

### 2. Запуск Mobile (Android Studio)
1. Відкрийте папку `mobile/` в Android Studio та дочекайтеся синхронізації Gradle.
2. Запустіть Android-емулятор (наприклад, `Small Phone API 30`).
3. Прокиньте порт локального сервера `8000` на емулятор через ADB:
   ```bash
   adb reverse tcp:8000 tcp:8000
   ```
4. Запустіть застосунок (`Run 'app'`). У `ApiService.kt` використовується адреса `http://127.0.0.1:8000/`.

## Контракт API (`POST /api/v1/listing`)
### Приклад запиту
```json
{
  "description": "Куртка Zara, розмір M, носив один сезон, дрібна потертість на рукаві",
  "condition": "good",
  "size": "M",
  "platform": "Grailed"
}
```
### Приклад успішної відповіді (`200 OK`)
```json
{
  "status": "ok",
  "category": "Куртки та верхній одяг",
  "condition": "good",
  "price_min": 410,
  "price_max": 550,
  "currency": "UAH",
  "title": "Куртка Zara, розмір M",
  "description": "Куртка Zara, розмір M, носив один сезон, дрібна потертість на рукаві / Size M. Condition: Used / 8/10. Category: Куртки та верхній одяг. Price: 410–550 UAH. #streetwear #archive #grailed #secondhand",
  "hint": null,
  "confidence": 0.9
}
```
Усі помилки (`422`, `502`, `504`) повертаються у єдиному форматі `{"error": "код", "message": "повідомлення"}` без технічного `stack trace`.
## Звіт із Лабораторної роботи 7 (Підсумкова інтеграція, тестування та демонстрація)

### 1. Інструкція встановлення debug-APK та локального запуску backend
- **Встановлення Android-застосунку (`app-debug.apk`):**
  1. Зберіть debug-APK за допомогою Gradle: `./gradlew assembleDebug` (файл буде створено в `mobile/app/build/outputs/apk/debug/app-debug.apk`).
  2. Встановіть APK на підключений Android-емулятор або фізичний пристрій через ADB:
     ```bash
     adb install mobile/app/build/outputs/apk/debug/app-debug.apk
     ```
- **Локальний запуск Backend (FastAPI):**
  1. Перейдіть у папку `backend/`:
     ```bash
     cd backend
     ```
  2. Встановіть залежності та налаштуйте `.env`:
     ```bash
     python -m pip install -r requirements.txt
     copy .env.example .env
     ```
  3. Запустіть серверну частину через Uvicorn:
     ```bash
     python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
     ```
  4. Прокиньте порт для емулятора Android:
     ```bash
     adb reverse tcp:8000 tcp:8000
     ```

### 2. Конфігурація без секретів
- Проєкт не містить жорстко закодованих токенів чи API-ключів.
- Усі налаштування винесені в клас `Settings` (`backend/app/core/config.py`) і читаються через змінні середовища з файлу `.env` (шаблон надано у `backend/.env.example`).
- За замовчуванням застосунок використовує детермінований `MockListingProvider`, який не вимагає external API keys для роботи. Для підключення реального LLM-провайдера достатньо вказати `AI_PROVIDER=real` та відповідний `AI_API_KEY` у локальному файлі `.env` (який ігнорується системою контролю версій).

### 3. Підсумок перевірок
- **Автоматизовані тести AI (`backend/test_ai.py`):** усі сценарії генерації, платформ (`OLX`, `eBay`, `Grailed`), брендів та дефектів проходять успішно (`Збіг`).
- **Архітектурні автотести (`backend/test_architecture.py`):** 6/6 тестів шаруватої архітектури, DI, обробки помилок та middleware пройдено (`ok`).
- **Мобільна збірка (`./gradlew assembleDebug`):** успішна збірка Android-застосунку з Jetpack Compose та Room Database.
- **Інтеграційне тестування:** перевірено роботу всіх станів UI, збереження в локальну базу даних, обробку таймаутів та мережевих помилок.

### 4. Відомі обмеження
- Правиловий характер `MockListingProvider` (словникова класифікація без зорового розпізнавання фото одягу).
- Локальне збереження даних виключно на пристрої у SQLite (Room Database) без хмарної синхронізації.
- Відсутність складних кеш-шарів у `RealListingProvider`.

### 5. Внесок Gemini CLI
- Автономне планування, аналіз та верифікація всієї кодової бази відповідно до інструкцій `docs/ai-instructions.md`.
- Формування комплексної технічної документації для ЛР7 без внесення ризикованих змін у робочий код (`backend/app/` та `mobile/app/src/main/java/`).
- Забезпечення високої якості тестування, збереження зворотної сумісності та підготовка демонстраційних матеріалів.

### 6. План 7–10-хвилинної демонстрації до захисту
1. **Вступ (1 хв):** Мета проєкту ReWear AI — автоматизація створення оголошень для секонд-хенду (OLX, eBay, Grailed).
2. **Демонстрація Backend (2 хв):** Запуск FastAPI, показ інтерактивної документації Swagger UI (`/docs`), демонстрація роботи `test_ai.py` та `test_architecture.py`.
3. **Демонстрація Mobile та UI станів (3 хв):** Встановлення debug-APK на емулятор, введення опису речі, генерація оголошення для різних маркетплейсів, демонстрація станів `Loading`, `Success` та обробки помилок.
4. **Демонстрація локальної історії (2 хв):** Перехід на вкладку «Історія», перегляд збережених у Room Database оголошень, деталі запису та копіювання в буфер обміну.
5. **Висновки та Q&A (2 хв):** Підсумок результатів Лабораторної роботи №7, архітектурних переваг та відповіді на запитання викладача.

## Звіт із Лабораторної роботи 6 (Варіант А — Розвиток AI-функціональності)

### 1. Обраний варіант і сценарій
- **Варіант:** **А (Розвиток AI-функціональності)** — вдосконалення правил `MockListingProvider` для врахування сегмента бренду (`brand_tier`), дефектів одягу та надання інтерактивних порад (`suggestions`) при низькій впевненості ШІ (`low_confidence`).
- **Функціональний сценарій:** генерація оголошення з розширеним аналізом бренду, стану та станом низької впевненості у мобільному інтерфейсі.

### 2. Користь зміни
Покращення якості оцінки вартості речей (врахування преміальних або мас-маркет брендів та наявних пошкоджень) та підвищення зручності користувача за рахунок інтерактивних швидких підказок (`suggestions`), які дозволяють в один клік уточнити опис при нерозпізнаній річі.

### 3. Опис реалізації
- **Backend (`backend/app/infrastructure/providers/mock_provider.py`, `schemas.py` тощо):**
  - **`brand_tier`:** класифікація бренду за словарем (luxury: Gucci, Prada, Balenciaga тощо з множником `1.8`; mid_range: Zara, Nike, Adidas з множником `1.0`; mass_market: Bershka, Pull&Bear тощо з множником `0.75`).
  - **Облік дефектів (`defect_multiplier`):** пошук слів-маркерів пошкоджень (потертість, пляма, дірка) з відповідними коефіцієнтами зниження ціни.
  - **`suggestions` та `low_confidence`:** у разі низької впевненості ШІ сервер формує не лише `hint`, а й список практичних підказок (`suggestions: list[str]`) для користувача.
- **Mobile (`mobile/app/src/main/java/com/rewear/ai/`):**
  - **`ListingModels.kt`:** додано поле `val suggestions: List<String>? = null` у моделі відповіді.
  - **`ListingViewModel.kt`:** передача підказок через доменну модель та `UiState.NoResult` / `LowConfidence`.
  - **`MainActivity.kt`:** відображення інтерактивних чіпів (`FilterChip`) із підказками під повідомленням про низьку впевненість, що дозволяє миттєво додати рекомендації до поля опису.

### 4. Таблиця контрольних прикладів
| № | Вхідні дані (опис, стан, платформа) | Очікуваний результат | Фактичний результат | Висновок |
|---|---|---|---|---|
| 1 | Куртка Gucci, розмір L, новий (`new`, `luxury`) | Категорія «Куртки», висока ціна з урахуванням luxury-множника (`1.8`) | Статус `ok`, `brand_tier: luxury`, ціна вища за базову | Збіг |
| 2 | Джинси Levi's, є пляма та невелика дірка (`fair`, дефекти) | Зниження цінового діапазону через `defect_multiplier` | Статус `ok`, ціна зменшена з урахуванням дефектів | Збіг |
| 3 | «щось дивне і незрозуміле» | Статус `low_confidence`, `hint`, список `suggestions` | `status: low_confidence`, сформовано `hint` та `suggestions` (чіпи в UI) | Збіг |

### 5. Перевірка попередньої функції
- Усі попередні функції збережено без регресій: базові сценарії ЛР2 (валідація, помилки 422/502/504), вибір платформ `OLX`, `eBay`, `Grailed` (ЛР3), локальна історія через Room Database (ЛР4), шарувата архітектура з DI та заголовок `X-Request-ID` (ЛР5).
- Автоматизовані тести (`python backend/test_ai.py`, `python backend/test_architecture.py`) та збірка `./gradlew assembleDebug` пройдені успішно.

### 6. Відомі обмеження
- Правиловий характер словників брендів і дефектів (бренди поза словником визначаються за замовчуванням).
- Евристичний характер розрахунку confidence та підказок.

### 7. Внесок Gemini CLI
- Планування розширення AI-функціональності, аналіз кодової бази відповідно до `docs/ai-instructions.md`, реалізація змін на backend та mobile без порушення зворотної сумісності та ретельна верифікація через автотести й Gradle.

---

## Звіт із Лабораторної роботи 5 (Варіант Б — FastAPI Backend Architecture)

### 1. Обраний варіант і сценарій
- **Варіант:** **Б (FastAPI Backend Architecture)** — реорганізація серверної частини без зміни HTTP-контракту та без регресії для мобільного клієнта.
- **Функціональний сценарій:** генерація картки оголошення (`POST /api/v1/listing`).

### 2. Три проблеми початкової реалізації
1. **Змішана відповідальність у HTTP-роутері (`backend/main.py`):** обробник `create_listing` одночасно валідував запит, містив тестові хуки (`__ai_error__`, `__bad_json__`), викликав AI-провайдер, перехоплював винятки та формував JSON-помилки.
2. **Жорстка залежність від конкретного провайдера (`backend/main.py`, `backend/ai_provider.py`):** роутер напряму інстанціював `MockProvider()` без абстрактного інтерфейсу, що унеможливлювало підміну провайдера через DI або тестування з fake-реалізацією.
3. **Відсутність типізованих доменних моделей і централізованої конфігурації:** `MockProvider.generate(...)` повертав нетипізований словник `dict`, а налаштування (`AI_PROVIDER`, `AI_MODEL`, `AI_API_KEY`, `AI_TIMEOUT_SEC`) не були винесені в окремий клас конфігурації.

### 3. Нова шарувата структура `backend/app/`
- **`core/config.py`:** централізований клас `Settings` для читання параметрів провайдера, моделі, ключа API, таймауту та прапорця fallback із `.env`.
- **`domain/`:** чисті доменні моделі `ListingCommand` і `ListingDraft` (`models.py`), ієрархія доменних винятків `DomainError` (`errors.py`) та контракт `ListingProvider(Protocol)` (`interfaces.py`).
- **`infrastructure/providers/`:** взаємозамінні реалізації `MockListingProvider` (правилова логіка), `RealListingProvider` (зовнішній LLM API через `httpx.AsyncClient`) та `FallbackListingProvider`.
- **`services/listing_service.py`:** прикладний сервіс `ListingService`, незалежний від FastAPI та Pydantic, який отримує `ListingProvider` через конструктор.
- **`api/`:** Pydantic-схеми та мапери (`schemas.py`), централізовані обробники винятків 422/502/504 (`error_handlers.py`), фабрики залежностей `FastAPI Depends` (`dependencies.py`) та тонкий роутер (`routes/listing.py`).

### 4. Контрольні розширення та результати автотестів
- **`FallbackListingProvider`:** провайдер-обгортка, яка при збої основного провайдера (`AiProviderDomainError` або `AiTimeoutDomainError`) автоматично перемикається на резервний провайдер і додає примітку в `hint`.
- **Наскрізний `X-Request-ID`:** HTTP middleware у `app/main.py` додає заголовок `X-Request-ID` у кожну відповідь та фіксує його у серверних логах.
- **Автоматизоване тестування (без реального зовнішнього API):**
   - `python backend/test_architecture.py` — **6/6 тестів `ok`** (перевірка `ListingService`, підміна залежностей через `app.dependency_overrides` для `504`/`502`, обробка помилок `RealListingProvider`, робота `FallbackListingProvider`, заголовок `X-Request-ID` та зворотна сумісність).
   - `python backend/test_ai.py` — **7/7 сценаріїв `Збіг`**.

**Висновок:** чисте розділення відповідальностей між роутером, прикладним сервісом, доменним контрактом та інфраструктурними провайдерами з DI через `FastAPI Depends` підвищило модульність, безпеку помилок і тестованість без реального зовнішнього API. Компромісом є збереження правилового `MockListingProvider` за замовчуванням для локальної роботи без платного ключа LLM API.

---

## Звіт із Лабораторної роботи 4 (Локальна історія через Room Database)

### 1. Вибір технологій та архітектура
- **Room Database (`2.7.1`)** разом із кодогенератором **KSP (`2.2.10-2.0.2`)** обрано як постійне SQLite-сховище Android, сумісне з Kotlin 2.2.10 та Android Gradle Plugin 9.5.1.
- Шар даних ізольовано від UI у пакеті `com.rewear.ai.data` (`HistoryEntity`, `HistoryDao`, `AppDatabase`, `HistoryRepository`) з доступом через `AndroidViewModel`.

### 2. Структура локального запису (`HistoryEntity`)
Таблиця `listing_history` зберігає: `id` (`Long`, автоінкремент), `createdAt` (`"yyyy-MM-dd HH:mm"`), `timestamp` (`Long`), `status` (`"готово"`), параметри входу (`description`, `condition`, `size`, `platform`) та результат AI (`category`, `title`, `resultDescription`, `priceMin`, `priceMax`, `currency`, `confidence`).

### 3. Правило збереження та фільтрація даних
- Запис додається до Room **тільки** коли `response.isSuccessful == true` і `body.status == "ok"`.
- **Що свідомо НЕ зберігається:** мережеві помилки, таймаути, помилки парсингу JSON (`JsonParseException`, `MalformedJsonException`), HTTP-помилки `422` / `502` / `504`, відповіді зі статусом `low_confidence`, а також секрети, токени чи технічні `stack trace`.
---

## Звіт із AI-Assisted розробки (ЛР3)

### 1. Порівняння планування: без Knowledge Base vs з Knowledge Base
Для задачі додавання вибору майданчика публікації (`OLX`, `eBay`, `Grailed`) було протестовано два підходи роботи coding-агента (`Gemini CLI`):

| Критерій порівняння | План №1 (без контексту `docs/` та `GEMINI.md`) | План №2 (з опорою на Knowledge Base `docs/`) |
|---|---|---|
| **Розуміння структури коду** | Поверхове: агент згадав неіснуючий маршрут «редагування лістингу» | Точне: вказано реальні 7 файлів (`models.py`, `main.py`, `ai_provider.py`, `test_ai.py`, `ListingModels.kt`, `ListingViewModel.kt`, `MainActivity.kt`) |
| **Розуміння AI-компонента** | Помилково запропонував «адаптувати промпти LLM», хоча в проєкті працює правиловий `MockProvider` | Коректно врахував правилову логіку `MockProvider.generate(...)` |
| **Зворотна сумісність API** | Не враховано — додавання обов'язкового поля зламало б старі клієнти | Передбачено дефолтне значення `platform = "OLX"` на рівні Pydantic та Kotlin DTO |
| **Аналіз ризиків і UI** | Відсутній | Описано ризик несумісності API та перевантаження мобільного екрана (вирішено через компактні `FilterChip`) |
| **План перевірки** | Не сформовано | Додано перевірку через Swagger UI, `test_ai.py` (зі зворотною сумісністю) та збірку Gradle |

### 2. Зафіксовані промпти та аналіз результатів
1. **Промпт 1 (План без Knowledge Base):**  
   `Не читай папку docs та файл GEMINI.md. Склади короткий технічний план додавання вибору майданчика публікації (OLX, eBay, Grailed) у проєкт ReWear AI (backend + mobile). Код поки що не змінюй.`  
   *Результат:* отримано загальний план із неточностями щодо маршрутів API та типу AI-провайдера.
2. **Промпт 2 (План із Knowledge Base):**  
   `Прочитай GEMINI.md та всю папку docs/, а також вивчи актуальний код у backend/ і mobile/. Склади детальний технічний план додавання вибору майданчика публікації (OLX, eBay, Grailed) відповідно до правил проєкту: вкажи точні файли, зміни в контрактах/моделях зі збереженням зворотної сумісності, ризики та план перевірки. Код поки що не змінюй.`  
   *Результат:* отримано точний покроковий план із урахуванням зворотної сумісності та тестування.
3. **Промпт 3 (Ізольована реалізація Backend):**  
   `Виконай крок 1 із твого плану — зміни ТІЛЬКИ backend (папку mobile поки що не чіпай): 1. У backend/models.py додай enum Platform... 2. У backend/main.py передай req.platform... 3. У backend/ai_provider.py онови generate... 4. У backend/test_ai.py додай перевірку всіх трьох платформ та збережи тест зворотної сумісності.`  
   *Результат:* оновлено серверні файли та тести. Під час перевірки запуску виявлено дефект (`AttributeError: Platform.OLX` при оголошенні `olx = "OLX"`).
4. **Промпт 4 (Виправлення дефекту та запуск автотестів):**  
   `Виправ помилку AttributeError у backend/models.py та backend/ai_provider.py: у класі Platform значення називається Platform.olx (маленькими літерами), а в коді використано Platform.OLX.`  
   *Результат:* агент узгодив імена атрибутів `Platform` (`OLX`, `eBay`, `Grailed`), перевів `test_ai.py` на `FastAPI TestClient` і підтвердив проходження всіх 7 тестових сценаріїв.
5. **Промпт 5 (Ізольована реалізація Mobile):**  
   `Виконай крок 2 із плану — онови ТІЛЬКИ мобільний застосунок у папці mobile/app/src/main/java/com/rewear/ai/ (папку backend не змінюй): 1. У ListingModels.kt додай поле val platform: String = "OLX"... 2. У ListingViewModel.kt онови метод generate... 3. У MainActivity.kt додай вибір майданчика публікації (OLX, eBay, Grailed) через compact Row з FilterChip.`  
   *Результат:* додано вибір майданчика на головному екрані Android-застосунку; функціонал перевірено на емуляторі для `OLX`, `eBay` та `Grailed`.

## Відомі обмеження та подальший розвиток

- AI-логіка за замовчуванням (`AI_PROVIDER=mock`) базується на словнику ключових слів українською мовою без виклику платного LLM API та аналізу фотографій.
- Відсутність офлайн-черги та хмарної синхронізації: локальна історія зберігається лише на пристрої у SQLite (Room).
- У мобільному клієнті впровадження DI-фреймворку (Hilt) та кешування відповідей у `RealListingProvider` залишаються як напрямки подальшого розвитку.

**Висновок:** використання проєктної Knowledge Base (`docs/` та `GEMINI.md`) усунуло галюцинації coding-агента щодо неіснуючих маршрутів і типу AI-моделі, дозволило одразу закласти зворотну сумісність API (`platform = "OLX"`) та розбити реалізацію на безпечні ізольовані кроки з автотестами.
