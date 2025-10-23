from pydantic_settings import BaseSettings
from datetime import datetime
from pathlib import Path

START_TIME = datetime.now()
TEAMS_FILE = Path("reference_data/all_teams.json")
VENUES_FILE = Path("reference_data/all_venues.json")

class Settings(BaseSettings):
    cfbd_base_url: str = "https://api.collegefootballdata.com"
    cfbd_api_key: str
    openai_api_key: str
    now: datetime = datetime.now()
    # API_TIMEOUT = 10
    # MAX_CONCURRENT_REQUESTS = 5

    class Config:
        env_file = ".env"

settings = Settings()
print(settings.now)