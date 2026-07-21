.PHONY: help install format format-check lint typecheck check ingest ask

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install dependencies via Poetry
	poetry install

format: ## Auto-format code (black + ruff --fix)
	poetry run black ingest.py ask.py
	poetry run ruff check --fix ingest.py ask.py

format-check: ## Check formatting without modifying files
	poetry run black --check ingest.py ask.py
	poetry run ruff check ingest.py ask.py

lint: ## Run ruff linter
	poetry run ruff check ingest.py ask.py

typecheck: ## Run mypy type checker
	poetry run mypy ingest.py ask.py

check: format-check lint typecheck ## Run all checks (format-check + lint + typecheck)

ingest: ## Ingest a PDF into the vector store (usage: make ingest PDF=docs/sample.pdf)
	poetry run python ingest.py "$(PDF)"

ask: ## Ask a question about an ingested PDF (usage: make ask PDF=docs/sample.pdf Q="question")
	poetry run python ask.py "$(PDF)" "$(Q)"
