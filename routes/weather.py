from fastapi import APIRouter
# from .deps import get_model_bundle  # loads model + featurizer
import asyncio
from services.cfbd_service import cfbd_service
router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("")
async def weather(start_year: int, end_year: int | None = None):
    end_year_to_use = end_year if end_year else start_year
    if end_year_to_use < start_year:
        return []
    years = range(start_year, end_year_to_use + 1)
    tasks = [cfbd_service.fetch_weather_for_year(year) for year in years]

    results = await asyncio.gather(*tasks)
    
    all_weather = []
    for year_data in results:
        all_weather.extend(year_data)
    # Add in game data massaging logic to map to Line class
    return all_weather