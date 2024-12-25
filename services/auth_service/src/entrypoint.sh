# services\auth_service\src\entrypoint.sh
set -e

echo "Applying migrations..."
alembic upgrade head

echo "Starting Auth Service..."
exec uvicorn src.app:app --host 0.0.0.0 --port 8002 --reload --log-level info
