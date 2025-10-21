import httpx
from config import settings

HEADERS = {
    "Authorization": f"Bearer {settings.cfbd_api_key}"
}
class CFBDService():
    async def fetch_games_for_year(self, year: int):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{settings.cfbd_base_url}/games?year={year}", headers=HEADERS)
                return response.json()
            except httpx.HTTPStatusError as e:
                # To improve
                print("HTTP status error")
                print(e)
            except Exception as e:
                # To improve
                print("general exception")
                print(e)

cfbd_service = CFBDService()