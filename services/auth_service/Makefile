# services\auth_service\Makefile
.PHONY: install run migrate

install:
	pip install --upgrade pip
	pip install -r requirements/base.txt

run:
	uvicorn src.app:app --host 0.0.0.0 --port 8002 --reload

migrate:
	alembic upgrade head
