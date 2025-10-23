import httpx
from fastapi import HTTPException
from config import settings
from pathlib import Path
import json

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
                    print("loading file cache")
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        # Save cache to the file
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    async def fetch_games_for_year(self, year: int):
        # Utilize the cache
        cache_key = f"games_{year}"
        if cache_key in self._cache:
            print(f"Cache hit for {year}")
            return self._cache[cache_key]
        
        print("Cache miss, calling API")
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
                print("HTTP status error")
                print(e)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching teams for year {year}: {str(e)}"
                )
    
    async def fetch_teams_for_year(self, year: int):
        """Fetch teams for a year with caching"""
        cache_key = f"teams_{year}"
        
        if cache_key in self._cache:
            print(f"Cache hit for {cache_key}")
            return self._cache[cache_key]
        
        print(f"Cache miss for {cache_key}, fetching from API...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.cfbd_base_url}/teams",
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
                print("HTTP status error")
                print(e)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching teams for year {year}: {str(e)}"
            )
    async def fetch_coaches_for_year(self, year: int):
        """Fetch teams for a year with caching"""
        cache_key = f"coaches_{year}"
        
        if cache_key in self._cache:
            print(f"Cache hit for {cache_key}")
            return self._cache[cache_key]
        
        print(f"Cache miss for {cache_key}, fetching from API...")
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
                print("HTTP status error")
                print(e)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching teams for year {year}: {str(e)}"
            )

cfbd_service = CFBDService()