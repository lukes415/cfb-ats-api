# cfb-ats-api

FastAPI backend serving college football ATS (against the spread) data and predictions. Sits between the CFBD (College Football Data) API and the `hate-watch-ios` mobile client.

## Running

```bash
uvicorn main:app --reload
```

Requires a `.env` file with:
```
CFBD_API_KEY=...
OPENAI_API_KEY=...
```

## Architecture

- `routes/` — one file per resource (games, teams, lines, coaches, venues, weather, chat)
- `services/cfbd_service.py` — all CFBD API calls; file-backed JSON cache at `cache.json` to avoid redundant API hits during dev
- `services/chat_service.py` — OpenAI function-calling endpoint for natural language CFB queries
- `services/model_loader.py` + `featurizer.py` — stubs for wiring in the ML model from `cfb-ats-data`; not yet connected to any route
- `schemas.py` — Pydantic models for all response types
- `reference_data/` — static JSON files for teams and venues (loaded at startup)

## What's mocked vs real

- `/health`, `/live` — real
- `/v1/games`, `/v1/lines`, `/v1/teams`, `/v1/coaches`, `/v1/venues`, `/v1/weather` — real (live CFBD data with caching)
- `/v1/teams/next-games` — real; used by `hate-watch-ios` to show upcoming games for selected teams
- `/v1/chat` — real (OpenAI function calling)
- `/score`, `/predict` (root level) — **mocked stubs**, not connected to the model yet

## Key notes

- `cfbd_service.py` mixes sync (`requests`) and async (`httpx`) — the sync methods (`fetch_venues`, `fetch_teams`) write to static reference files and are only called during setup, not per-request
- Cache is keyed by resource + year (e.g. `games_2024`); no TTL — clear `cache.json` manually to force a refresh
- The `Game` schema in `schemas.py` has many optional fields intended for ML feature engineering, not direct API passthrough

## Related projects

- `../cfb-ats-data` — produces the ML model and featurizer artifacts consumed here
- `../hate-watch-ios` — iOS client; calls `/v1/teams/next-games` to display upcoming games for tracked teams
