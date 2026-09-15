.PHONY: check test

check:
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy src/unitree_rl_unilab

test:
	uv run pytest
