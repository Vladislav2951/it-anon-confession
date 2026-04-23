# it-anon-confession

Демонстрационный проект backend-сервера платформы анонимных признаний IT-специалистов, реализованный с использованием FastAPI, SQLAlchemy 2.0 (PostgreSQL + Alembic).

## Основные возможности

* **Аутентификация на сессиях:** Безопасное хранение сессий в БД, передача через HttpOnly куки.
* **Система RBAC:** Управление доступом на основе ролей и разрешений (Permissions) для каждого бизнес-элемента.
* **Управление признаниями:** Создание, чтение, обновление и удаление анонимных записей.
* **Админ-панель:** Инструменты для управления пользователями, ролями и мониторинга разрешений.
* **Безопасность:** Валидация входных данных, очистка HTML-тегов (Sanitization), хеширование паролей (Bcrypt), CORS.

## Технологический стек

* **Фреймворк:** FastAPI
* **База данных:** PostgreSQL + SQLAlchemy 2.0 (Async)
* **Миграции:** Alembic
* **Валидация:** Pydantic v2
* **Тестирование:** pytest + coverage
* **Логирование:** стандартный модуль logging
* **Пакетный менеджер:** UV
* **Контейнеризация:** Docker + Docker Compose
* **Дополнительные средства:**
  * форматирование кода: Black + isort
  * статический анализ типов: MyPy

## Установка и запуск

### Требования

* Docker и Docker Compose
* UV
* Python 3.13+ (если запуск локально)

### Быстрый старт (Docker)

1. Скопируйте окружение:

    ```bash
    cp example.env .env
    ```

2. Запустите проект:

    ```bash
    docker-compose up --build
    ```

3. API будет доступно по адресу: `http://localhost:8000`
4. Документация Swagger: `http://localhost:8000/docs`

### Локальная разработка

1. Установите пакетный менеджер UV:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. Установите зависимости:

    ```bash
    uv sync
    ```

3. Запустите PostgreSQL (например, через Docker)
4. Примените миграции: `prestart.sh`
  или

   ```bash
   alembic upgrade head
   ```

5. Запустите сервер:

    ```bash
    uvicorn src.main:app --reload
    ```

### Тестирование

Для запуска тестов использовать команду:

  ```bash
  uv run pytest -v .
  ```

## Краткая документация API

## Аутентификация (/auth)

Все запросы, кроме регистрации и входа, требуют наличия куки `session_id`.

* **POST** `/auth/register` — Регистрация нового аккаунта  
* **POST** `/auth/login` — Вход в систему (устанавливает HttpOnly куку)  
* **POST** `/auth/logout` — Завершение сессии и удаление куки  

---

## Пользователи (/users)

* **GET** `/users/{identifier}` — Получение публичного профиля (по UUID или Email)  
* **PATCH** `/users/{user_id}` — Частичное обновление своих данных (nickname, bio)  
* **POST** `/users/{user_id}/change-password` — Смена пароля (требует старый пароль)  
* **DELETE** `/users/me` — Удаление собственного аккаунта ("мягкое" удаление)  

---

## Признания (/confessions)

* **POST** `/confessions/` — Создать новое анонимное признание  
* **GET** `/confessions/` — Список всех признаний
* **GET** `/confessions/{id}` — Детали конкретного признания  
* **PATCH** `/confessions/{id}` — Редактирование текста
* **DELETE** `/confessions/{id}` — Удаление признания  

---

## Администрирование (/admin)

Требуется соответствующие разрешения на бизнес-элемент `admin`.

### Управление пользователями

* **GET** `/admin/users/` — Список всех зарегистрированных пользователей  
* **DELETE** `/admin/users/{user_id}` — Принудительное удаление пользователя  
* **GET** `/admin/users/{user_id}/permissions` — Просмотр всех прав пользователя  
* **POST** `/admin/users/{user_id}/assign-role/{role_id}` — Назначить роль пользователю  
* **POST** `/admin/users/{user_id}/revoke-role/{role_id}` — Отозвать роль у пользователя  

### Управление ролями и правами

* **GET** `/admin/roles/` — Список всех ролей  
* **POST** `/admin/roles/` — Создание новой роли  
* **PATCH** `/admin/roles/{id}` — Переименование роли (кроме системных)  
* **DELETE** `/admin/roles/{id}` — Удаление роли (кроме системных)
* **POST** `/admin/roles/{id}/assign-permission/{pid}` — Назначить разрешение роли  
* **POST** `/admin/roles/{id}/revoke-permission/{pid}` — Убрать разрешение у роли  
* **GET** `/admin/permissions/` — Список всех разрешений системы  
* **GET** `/admin/business-elements/` — Список бизнес-элементов системы  

## Типовые коды ошибок

* **400 CONFLICT** — Некорректный запрос.
* **401 UNAUTHORIZED** — Сессия отсутствует, истекла или невалидна.
* **403 FORBIDDEN** — Недостаточно прав для выполнения операции (например, доступ обычного пользователя к `/admin`, либо попытка удалить последнего администратора).
* **409 CONFLICT** — Конфликт состояния ресурса (например, регистрация с уже существующим email).
* **422 UNPROCESSABLE ENTITY** — Ошибка валидации данных  

## Структура проекта

Структура проекта с описанием основных элементов:

```text
.              
├── prestart.sh               # Скрипт запуска миграций
├── pyproject.toml            # Зависимости и настройки проекта (UV)
├── src                       # Основной исходный код приложения
│   ├── api                   # Слой API
│   │   └── http
│   │       ├── common_exceptions.py  # Общие HTTP-ошибки
│   │       ├── dto/                  # DTO для API слоя
│   │       ├── endpoints             # HTTP-эндпоинты
│   │       │   ├── admin/            # Админские маршруты
│   │       │   ├── auth.py           # Аутентификация
│   │       │   ├── confessions.py    # Работа с "confessions"
│   │       │   └── users.py          # Работа с пользователями
│   │       ├── middleware/           # Middleware (авторизация, контекст)
│   │       ├── response_models.py    # Модели ответов API
│   │       └── routes.py             # Регистрация маршрутов
│   ├── core                 # Общие настройки и инфраструктурные зависимости
│   │   ├── config.py        # Конфигурация приложения (env, settings)
│   │   ├── dependencies.py  # DI
│   │   └── security.py      # Утилиты безопасности
│   ├── domain               # Домен
│   │   ├── dto/             # DTO доменного уровня
│   │   ├── entities/        # Сущности (бизнес-модели)
│   │   ├── enums/           # Перечисления
│   │   ├── errors.py        # Доменные ошибки
│   │   ├── interfaces/      # Интерфейсы (репозитории, UoW)
│   │   │   └── database
│   │   │       ├── *_repo.py    # Контракты репозиториев
│   │   │       ├── filters/     # Фильтры для запросов
│   │   │       └── uow.py       # Unit of Work интерфейс
│   │   └── validators.py    # Валидация бизнес-логики
│   ├── infrastructure       # Реализация инфраструктуры
│   │   └── postgres
│   │       ├── db.py         # Подключение к PostgreSQL
│   │       ├── models/       # ORM модели (SQLAlchemy)
│   │       ├── repositories/ # Реализация репозиториев
│   │       └── uow.py        # Реализация Unit of Work
│   ├── libs                  # Вспомогательные библиотеки
│   │   └── logger/           # Кастомный логгер
│   ├── main.py               # Точка входа приложения
│   ├── migrations/           # Миграции (Alembic)
│   └── services/             # Use cases / бизнес-логика
└── tests/                    # Тесты
```

## Схема базы данных

![diagram](docs/images/postgres-diagram.png)

## Примеры запросов

### Регистрация

  Запрос:

  ```bash
  curl -X POST http://localhost:8000/auth/register \
      -H "Content-Type: application/json" \
      -d '{
        "email": "dev@example.com",
        "password": "strong_password_123",
        "password_repeat": "strong_password_123",
        "nickname": "bug_hunter",
        "bio": "I write bugs for food"
      }'
  ```

  Ответ (201 Created):

  ```bash
  {
    "message": "User has been registered"
  }
  ```

### Признания

  Запрос:

  ```bash
  curl -X POST http://localhost:8000/confessions/ \
      --cookie "session_id=<your_session_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "title": "Prod Disaster",
        "body": "I accidentally dropped the production database on Friday evening."
      }'
  ```

  Ответ (200 OK):

  ```json
  {
    "data": {
      "id": "019ca1e5-c378-7000-8000-000000000405",
      "title": "Prod Disaster",
      "body": "I accidentally dropped the production database on Friday evening.",
      "authored_by": "bug_hunter",
      "created_at": "2026-04-23T14:20:00Z"
    }
  }
  ```

### Пользователи

  Запрос:

  ```bash
  curl -X GET http://localhost:8000/users/019ca1e5-c378-7000-8000-000000000201 \
      --cookie "session_id=<your_session_token>"
  ```

  Ответ (200 OK):

  ```json
  {
    "data": {
      "id": "019ca1e5-c378-7000-8000-000000000201",
      "email": "admin@example.com",
      "nickname": "admin",
      "bio": "Administrator"
    }
  }
  ```

  Ошибка (403 FORBIDDEN):

  ```json
  {
    "detail": {
      "code": "FORBIDDEN",
      "message": "Access denied"
    }
  }
  ```
