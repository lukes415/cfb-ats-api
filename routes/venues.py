import json
from fastapi import APIRouter
from pathlib import Path
from services.cfbd_service import cfbd_service
from datetime import datetime
from config import VENUES_FILE

router = APIRouter(prefix="/venues", tags=["venues"])

@router.get("")
def teams(year: int | None = None):
    year_to_use = datetime.now().year if not year else year
    try:
        with open(VENUES_FILE, "r") as f:
            data = json.load(f)
        return [t for t in data]
    except FileNotFoundError:
        print(f"Teams file not found, fetching from API")
        return cfbd_service.fetch_venues(year_to_use)
