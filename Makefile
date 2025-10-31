PYTHON = python3

.PHONY: lint
lint:
	@echo "Запуск ruff..."
	ruff format .
	@echo "Запуск ruff check --fix..."
	ruff check --fix
	@echo "Запуск mypy..."
	mypy app/ scripts/
