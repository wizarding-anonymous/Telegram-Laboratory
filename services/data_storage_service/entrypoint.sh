#!/usr/bin/env bash

# Остановка скрипта при любой ошибке
set -e

# 1. Установка зависимостей (опционально)
# Если вы уже устанавливаете зависимости в Dockerfile, то это можно пропустить
# echo "Installing Python dependencies..."
# pip install --no-cache-dir -r requirements.txt

# 2. Применение миграций Alembic
echo "Applying migrations..."
alembic upgrade head

# 3. Запуск приложения (Uvicorn / Gunicorn + UvicornWorker / etc.)
# Здесь показываем пример с Uvicorn
echo "Starting the Data Storage Service..."
exec uvicorn src.app:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    --log-level info