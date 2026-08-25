# Segstream Take home exam

## Setup

Python 3.14 and [`uv`](https://docs.astral.sh/uv/) are expected.

```bash
uv sync --dev
uv run python manage.py migrate
```

### Load the sample data

Run this after `migrate`:

```bash
uv run python manage.py loaddata sample_data
```

You only need to load it once for each new database.

## Run

```bash
uv run python manage.py runserver
```

## Verify

```powershell
uv run ruff check .
uv run ruff format --check .
```
