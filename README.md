# URL Shortener API

Lightweight URL shortener with in-memory storage.

## Setup

```bash
pip install -r requirements.txt
python shortener.py
```

Server runs at http://localhost:5000

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /shorten | Shorten a URL |
| GET | /<code> | Redirect to original URL |
| GET | /stats/<code> | Get URL info without redirect |
| GET | /health | Health check |

## Usage

```bash
curl -X POST http://localhost:5000/shorten -H 'Content-Type: application/json' -d '{"url": "https://example.com"}'
curl -L http://localhost:5000/AbCd12
curl http://localhost:5000/stats/AbCd12
```

## Features

- Base62 short codes (6 chars)
- Deduplication (same URL = same code)
- Input validation (HTTP/HTTPS only, max 2048 chars)
- Health check endpoint

## Tests

```bash
pytest test_shortener.py -v
```
