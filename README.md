# BookRentAPI

REST API for managing a book catalog and rentals. Stack: FastAPI, SQLAlchemy (async), PostgreSQL, Alembic.

## Local setup with Docker

### 1. Environment

```bash
cp .env.example .env
```

Fill in `.env` with your values (see below).

### 2. Start PostgreSQL

```bash
docker compose up -d
```

The database will be available at `localhost:5432`.

### 3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

App: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Swagger docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Environment variables

Copy `.env.example` to `.env` and set the values:

| Variable | Description |
|----------|-------------|
| `DB_HOST` | PostgreSQL host (`localhost` when using Docker) |
| `DB_PORT` | PostgreSQL port (default `5432`) |
| `DB_USER` | Database user |
| `DB_PASS` | Database password |
| `DB_NAME` | Database name |
| `SECRET_KEY` | JWT secret key (long random string) |
| `ALGORITHM` | JWT algorithm (usually `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token lifetime in minutes |

## Shutdown

```bash
docker compose down
```

Database data is kept in the Docker volume `pgdata`. To remove it as well: `docker compose down -v`.
