# Repository Guidelines

## Project Structure & Module Organization
- `src/`: application code (e.g., `iot_calendar.py`, `calendar_image.py`).
- `tests/`: pytest test suite and fixtures.
- `templates/` and `static/`: HTML, CSS, JS, and images served by Tornado.
- `docker/`: Dockerfile and bundled fonts.
- `docs/`: MkDocs config and sources.
- `scripts/`: helper scripts (requirements, docs).
- Private config and secrets live outside the repo in `../amazon-dash-private/`.

## Build, Test, and Development Commands
- Build image: `make build` (uses `docker/Dockerfile`).
- Run locally in Docker: `make run` (exposes `http://localhost:4444`).
- Run tests: `make test` or `python -m pytest tests/`.
- Benchmarks: `make bench` or `pytest -m benchmark`.
- Update requirements: `make reqs` (uv + pip-compile flow).
- Docs preview: `make docs` (English) or `make docs-ru`.
- Local debug (without Docker): `. ./activate.sh` then `python src/iot_calendar.py --port=4444 folder=../amazon-dash-private`.

## Coding Style & Naming Conventions
- Formatter/linter: Ruff via pre-commit; line length 99–100.
- Typing: Mypy enabled; prefer explicit types for public APIs.
- Indentation: 4 spaces; follow PEP 8 (snake_case for functions/vars, CamelCase for classes, UPPER_CASE for constants).
- Lint config: see `.ruff.toml`, `.flake8`, and `.pylintrc` (tests are relaxed).

## Testing Guidelines
- Framework: Pytest with doctests enabled (`pytest.ini`).
- Naming: place tests in `tests/` as `test_*.py`.
- Run unit tests: `pytest -m "not benchmark"`.
- Benchmarks: mark with `@pytest.mark.benchmark`; run via `pytest -m benchmark`.
- Coverage: optional; example `pytest --cov=src --cov-report=term-missing` (see `.coveragerc`).

## Commit & Pull Request Guidelines
- Commits: concise, imperative mood (e.g., "fix lint", "add benchmark"); group related changes.
- PRs: include a clear description, linked issues, and notable screenshots (e.g., calendar image) when UI/visuals change.
- Quality gate: run `pre-commit run --all-files` and `pytest` before opening/merging.

## Security & Configuration Tips
- Do not commit secrets. Keep Google credentials and OpenWeatherMap key in `../amazon-dash-private/` and share the calendar with the service account.
- For container runs, ensure the folder is mounted/readable as in `make run`.
