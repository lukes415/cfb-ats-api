import httpx
import asyncio
import logging
from fastapi import HTTPException
from config import settings
from pathlib import Path
import json
from config import TEAMS_FILE, VENUES_FILE
import requests
from schemas import Team
from datetime import datetime, timezone, date, timedelta

logger = logging.getLogger(__name__)

CFBD_BASE_URL = settings.cfbd_base_url
HEADERS = {
    "Authorization": f"Bearer {settings.cfbd_api_key}"
}
class CFBDService():
    def __init__(self):
        self.cache_file = Path("cache.json")
        self._cache = self._load_cache()
    
    def _load_cache(self):
        # Load cache if exists to prevent extra calls during testing/dev
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    logger.debug("loading file cache")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        # Save cache to the file
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    async def fetch_games_for_year(self, year: int):
        # Utilize the cache
        cache_key = f"games_{year}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for {year}")
            return self._cache[cache_key]
        
        logger.debug("Cache miss, calling API")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.cfbd_base_url}/games",
                    params={"year": year},
                    headers=HEADERS
                    #add timeout
                )
                response.raise_for_status()
                data = response.json()
                self._cache[cache_key] = data
                self._save_cache()
                return data
            except httpx.HTTPStatusError as e:
                # To improve
                logger.error(f"HTTP status error: {e}")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching games for year {year}: {str(e)}"
                )
    
    async def fetch_teams_for_year(self, year: int):
        """Fetch teams for a year with caching"""
        cache_key = f"teams_{year}"
        
        if cache_key in self._cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self._cache[cache_key]
        
        logger.debug(f"Cache miss for {cache_key}, fetching from API...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.cfbd_base_url}/teams",
                    params={"year": year},
                    headers=HEADERS,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                # Store in cache and save to file
                self._cache[cache_key] = data
                self._save_cache()
                return data
        except httpx.HTTPStatusError as e:
                # To improve
                logger.error(f"HTTP status error: {e}")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching teams for year {year}: {str(e)}"
            )
    async def fetch_coaches_for_year(self, year: int):
        """Fetch teams for a year with caching"""
        cache_key = f"coaches_{year}"
        
        if cache_key in self._cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self._cache[cache_key]
        
        logger.debug(f"Cache miss for {cache_key}, fetching from API...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.cfbd_base_url}/coaches",
                    params={"year": year},
                    headers={"Authorization": f"Bearer {settings.cfbd_api_key}"},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                # Store in cache and save to file
                self._cache[cache_key] = data
                self._save_cache()
                return data
        except httpx.HTTPStatusError as e:
                # To improve
                logger.error(f"HTTP status error: {e}")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching coaches for year {year}: {str(e)}"
            )

    def fetch_venues(self, year: int):
        VENUES_FILE.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(
            f"{CFBD_BASE_URL}/venues",
            params={"year": year},
            headers = HEADERS,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        with open(VENUES_FILE, "w") as f:
            json.dump(data, f, indent=2)
        
        return [venue for venue in data]
    
    def fetch_teams(self, year: int):
        TEAMS_FILE.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(
            f"{CFBD_BASE_URL}/teams",
            params={"year": year},
            headers = HEADERS,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        with open(TEAMS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        
        return [team for team in data]

    async def fetch_lines_for_year(self, year: int):
        # Utilize the cache
        cache_key = f"lines_{year}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for {year}")
            return self._cache[cache_key]
        
        logger.debug("Cache miss, calling API")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.cfbd_base_url}/lines",
                    params={"year": year},
                    headers=HEADERS
                    #add timeout
                )
                response.raise_for_status()
                data = response.json()
                self._cache[cache_key] = data
                self._save_cache()
                return data
            except httpx.HTTPStatusError as e:
                # To improve
                logger.error(f"HTTP status error: {e}")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching lines for year {year}: {str(e)}"
                )
    async def fetch_weather_for_year(self, year: int):
        # Utilize the cache
        cache_key = f"weather_{year}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for {year}")
            return self._cache[cache_key]

        logger.debug("Cache miss, calling API")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.cfbd_base_url}/games/weather",
                    params={"year": year},
                    headers=HEADERS
                    #add timeout
                )
                response.raise_for_status()
                data = response.json()
                self._cache[cache_key] = data
                self._save_cache()
                return data
            except httpx.HTTPStatusError as e:
                # To improve
                logger.error(f"HTTP status error: {e}")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching weather for year {year}: {str(e)}"
                )

    async def fetch_elo_for_week(self, year: int, week: int) -> list:
        """
        Fetch pregame ELO ratings for all teams for a given season week.

        ELO updates retroactively as the season progresses, so we key the cache
        by the current Monday (not week number) to ensure ratings reflect all
        completed games through last weekend.
        """
        monday = _monday_cache_key()
        cache_key = f"elo_{year}_{monday}"

        if cache_key in self._cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self._cache[cache_key]

        logger.debug(f"Cache miss for {cache_key}, fetching ELO from API...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.cfbd_base_url}/ratings/elo",
                    params={"year": year, "week": week},
                    headers=HEADERS,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                self._cache[cache_key] = data
                self._save_cache()
                return data
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching ELO: {e}")
                return []
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error fetching ELO: {str(e)}")

    async def fetch_game_details(self, game_id: str, game_date: str, year: int) -> dict:
        """
        Fetch and cache enriched game details: venue_id, weather, and lines.

        We store venue_id (not the full venue object) because venue data is
        static and already cached separately in all_venues.json.

        Invalidation: refetch if 3+ days old OR game is within 2 days.
        See _game_cache_needs_refresh for rationale.
        """
        cache_key = f"game_{game_id}"
        entry = self._cache.get(cache_key)

        if entry and not _game_cache_needs_refresh(entry):
            logger.debug(f"Cache hit for {cache_key}")
            return entry

        logger.debug(f"Fetching game details for game {game_id}...")

        async with httpx.AsyncClient() as client:
            weather_task = client.get(
                f"{settings.cfbd_base_url}/games/weather",
                params={"year": year, "gameId": game_id},
                headers=HEADERS,
                timeout=30
            )
            lines_task = client.get(
                f"{settings.cfbd_base_url}/lines",
                params={"year": year, "gameId": game_id},
                headers=HEADERS,
                timeout=30
            )
            weather_resp, lines_resp = await asyncio.gather(
                weather_task, lines_task, return_exceptions=True
            )

        weather_data = {}
        if not isinstance(weather_resp, Exception):
            weather_resp.raise_for_status()
            w_list = weather_resp.json()
            if w_list:
                w = w_list[0]
                weather_data = {
                    "temperature": w.get("temperature"),
                    "conditions": w.get("weatherCondition"),
                    "wind_mph": w.get("windSpeed"),
                }

        lines_data = {}
        venue_id = None
        if not isinstance(lines_resp, Exception):
            lines_resp.raise_for_status()
            l_list = lines_resp.json()
            if l_list:
                game_lines = l_list[0]
                venue_id = game_lines.get("venueId")
                book_lines = game_lines.get("lines", [])
                # Prefer consensus line; fall back to first available provider
                consensus = next((l for l in book_lines if l.get("provider") == "consensus"), None)
                chosen = consensus or (book_lines[0] if book_lines else None)
                if chosen:
                    lines_data = {"spread": chosen.get("spread")}

        now = datetime.now(timezone.utc)
        entry = {
            "cached_at": now.isoformat(),
            "game_date": game_date,
            "venue_id": venue_id,
            "weather": weather_data,
            "lines": lines_data,
        }
        self._cache[cache_key] = entry
        self._save_cache()
        return entry


def _monday_cache_key() -> str:
    """
    Returns the ISO date string of the most recent Monday.

    We key ELO cache entries by Monday because CFB games run Thursday–Sunday
    and ELO ratings update retroactively as results come in. By Monday, the
    previous week's ELO is finalized and should be relatively stable until
    the next game.
    """
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat()


def _game_cache_needs_refresh(entry: dict) -> bool:
    """
    Returns True if the game details cache entry should be refetched.

    Two conditions trigger a refresh (either one is sufficient):
    - Entry is 3+ days old: weather and lines can drift meaningfully over 3 days.
    - Game is within 2 days: we want the freshest data as game day approaches,
      since weather forecasts tighten and lines can move sharply in the final 48h.

    This avoids hammering the CFBD API for games 2+ weeks out where stale
    weather and lines are fine — nobody cares about a forecast 3 weeks away.
    """
    now = datetime.now(timezone.utc)
    cached_at = datetime.fromisoformat(entry["cached_at"].replace("Z", "+00:00"))
    game_date = datetime.fromisoformat(entry["game_date"].replace("Z", "+00:00"))

    age_days = (now - cached_at).total_seconds() / 86400
    days_until_game = (game_date - now).total_seconds() / 86400

    return age_days >= 3 or days_until_game <= 2


cfbd_service = CFBDService()