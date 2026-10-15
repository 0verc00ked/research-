.PHONY: install test lint typecheck fmt backtest probe-contamination clean

install:
	uv sync --all-extras

test:
	uv run pytest

lint:
	uv run ruff check .

typecheck:
	uv run mypy agent_trader strategies

fmt:
	uv run ruff format .
	uv run ruff check --fix .

backtest:
	@echo "TODO: wire to agent_trader.backtest.runner once a strategy lands G0"
	@exit 1

probe-contamination:
	@echo "Running V-9 contamination probes — requires API key in .env"
	uv run python research/phase2_evidence/contamination_probe.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache dist build *.egg-info
