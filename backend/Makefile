UV = uv run
APP_MODULE = src.main:app

.PHONY: help install run migrate revisions lint test clean

# uv
install:
	uv sync


# uvicorn
run:
	$(UV) uvicorn $(APP_MODULE) --port 8000



# alembic
migrate:
	$(UV) alembic upgrade head

downgrade:
	$(UV) alembic downgrade -1

revision:
	$(UV) alembic revision --autogenerate -m "$(msg)"



# test
test: 
	$(UV) pytest -q


# clean
lint: 
	$(UV) ruff check src tests --fix
	$(UV) ruff format src tests
