# apps/backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy application
COPY . .

# Run migrations and start server
CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}

# apps/backend/render.yaml
services:
  - type: web
    name: finance-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install poetry && poetry install
    startCommand: alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: finance-db
          property: connectionString
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_JWT_SECRET
        sync: false
      - key: GOOGLE_CLIENT_ID
        sync: false
      - key: GOOGLE_CLIENT_SECRET
        sync: false
      - key: GMAIL_WEBHOOK_SECRET
        generateValue: true
      - key: TZ
        value: America/Santiago

# apps/backend/.dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.pytest_cache
.coverage
htmlcov
.env
.venv
venv/
