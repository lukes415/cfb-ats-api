import httpx
from config import settings

HEADERS = {
    "Authorization": f"Bearer {settings.cfbd_api_key}"
}

async def fetch_games_for_year(year: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.cfbd_base_url}/games?year={year}", headers=HEADERS)
            return response.json()
        except httpx.HTTPStatusError as e:
            # Flesh this out
            print("HTTP status error")
            print(e)
        except Exception as e:
            #Flesh this out
            print("general exception")
            print(e)