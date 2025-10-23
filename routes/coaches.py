from fastapi import APIRouter
# from .deps import get_model_bundle  # loads model + featurizer
import asyncio
from services.cfbd_service import cfbd_service
import json
router = APIRouter(prefix="/coaches", tags=["coaches"])

@router.get("")
async def coaches(start_year: int, end_year: int | None = None):
    end_year_to_use = end_year if end_year else start_year
    if end_year_to_use < start_year:
        return []
    years = range(start_year, end_year_to_use + 1)
    tasks = [cfbd_service.fetch_coaches_for_year(year) for year in years]

    all_coaches = []
    results = await asyncio.gather(*tasks)
    for year_data in results:
        all_coaches.extend(year_data)
    # Add in game data massaging logic to map to Coach class
    return all_coaches
