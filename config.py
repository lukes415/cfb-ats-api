from pydantic_settings import BaseSettings
from datetime import datetime
from pathlib import Path

START_TIME = datetime.now()
TEAMS_FILE = Path("reference_data/all_teams.json")
VENUES_FILE = Path("reference_data/all_venues.json")

# Path to the exported sklearn Pipeline from cfb-ats-data.
# Defaults to the sibling repo's models/ directory for local dev.
# Override via MODEL_PATH env var if the repos live in different locations.
MODEL_PATH = Path("../cfb-ats-data/models/cfb_ats_model.joblib")

class Settings(BaseSettings):
    cfbd_base_url: str = "https://api.collegefootballdata.com"
    cfbd_api_key: str
    openai_api_key: str
    now: datetime = datetime.now()

    # Feature flag: set to false in .env to disable predictions even if the model
    # file is present — useful during development or after a bad model retrain.
    predictions_enabled: bool = True

    class Config:
        env_file = ".env"

settings = Settings()