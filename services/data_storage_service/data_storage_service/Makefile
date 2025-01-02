.PHONY: install run migrate test format lint

install:
	pip install --upgrade pip
	pip install -r requirements.txt

run:
	uvicorn src.app:app --host 0.0.0.0 --port 8001 --reload

migrate:
	alembic upgrade head

test:
	pytest -v --cov=src --cov-report term-missing tests/

format:
	black src tests

lint:
	flake8 src tests