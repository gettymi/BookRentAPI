# BookRentAPI

REST API для управления каталогом книг и их арендой. Стек: FastAPI, SQLAlchemy (async), PostgreSQL, Alembic.

## Локальный запуск через Docker

### 1. Подготовка окружения

```bash
cp .env.example .env
```

Заполните `.env` своими значениями (см. раздел ниже).

### 2. Запуск PostgreSQL

```bash
docker compose up -d
```

База будет доступна на `localhost:5432`.

### 3. Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Миграции

```bash
alembic upgrade head
```

### 5. Запуск API

```bash
uvicorn app.main:app --reload
```

Приложение: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Документация Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Переменные окружения

Скопируйте `.env.example` в `.env` и задайте значения:

| Переменная | Описание |
|------------|----------|
| `DB_HOST` | Хост PostgreSQL (`localhost` при Docker) |
| `DB_PORT` | Порт PostgreSQL (по умолчанию `5432`) |
| `DB_USER` | Имя пользователя БД |
| `DB_PASS` | Пароль пользователя БД |
| `DB_NAME` | Имя базы данных |
| `SECRET_KEY` | Секретный ключ для JWT (длинная случайная строка) |
| `ALGORITHM` | Алгоритм JWT (обычно `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access-токена в минутах |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Время жизни refresh-токена в минутах |

## Остановка

```bash
docker compose down
```

Данные БД сохраняются в Docker volume `pgdata`. Чтобы удалить и их: `docker compose down -v`.
