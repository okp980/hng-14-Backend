# Stage 1 — Name Gender Classification API (FastAPI)

A small FastAPI service that exposes a single endpoint to **classify a given name** by calling the **Genderize API** and returning a processed, structured response (including `sample_size`, `is_confident`, and a `processed_at` timestamp).

## API

- **Endpoint**: `GET /api/classify?name={name}`
- **Health/root**: `GET /` (returns a simple hello message)

### Success response (example)

```json
{
  "status": "success",
  "data": {
    "name": "john",
    "gender": "male",
    "probability": 0.99,
    "sample_size": 1234,
    "is_confident": true,
    "processed_at": "2026-04-01T12:00:00+00:00"
  }
}
```

### Error responses

All errors follow:

```json
{ "status": "error", "message": "" }
```

Common cases:

- `400`: Missing or empty `name` parameter
- `422`: `name` is not a string
- If Genderize returns no prediction (`gender: null` or `count: 0`): `status=error` with message `"No prediction available for the provided name"`

## Prerequisites

- **Python**: 3.13+
- **Genderize API key**: set `GENDERIZE_API_KEY` in your environment (see below)

## Setup

Create a `.env` file (do not commit it):

```bash
cp .env.sample .env
```

Then edit `.env` and set:

```bash
GENDERIZE_API_KEY=your_api_key_here
```

## Run locally

This project uses `pyproject.toml`. If you have [`uv`](https://docs.astral.sh/uv/) installed:

```bash
uv sync
uv run fastapi dev main.py
```

If you prefer `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install "fastapi[standard]" httpx python-dotenv
fastapi dev main.py
```

By default, FastAPI will start on `http://127.0.0.1:8000`.

## Try it

```bash
curl "http://127.0.0.1:8000/"
```

```bash
curl "http://127.0.0.1:8000/api/classify?name=john"
```

Interactive docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

