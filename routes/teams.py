import json
from fastapi import APIRouter
from pathlib import Path
import requests
from config import settings
from schemas import Team
from services.cfbd_service import cfbd_service
from datetime import datetime

CURR_YEAR = datetime.now().year

TEAMS_FILE = Path("reference_data/all_teams.json")

router = APIRouter(prefix="/teams", tags=["teams"])

@router.get("")
def teams(year: int | None = None):
    year_to_use = CURR_YEAR if not year else year
    try:
        with open(TEAMS_FILE, "r") as f:
            data = json.load(f)
        return [t for t in data]
    except FileNotFoundError:
        print(f"Teams file not found, fetching from API")
        return cfbd_service.fetch_teams(year_to_use)

