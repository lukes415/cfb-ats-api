from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# load_dotenv()
# print("API key", os.getenv("cfbd_api_key"))

class Settings(BaseSettings):
    cfbd_base_url: str = "https://api.collegefootballdata.com"
    cfbd_api_key: str
    # API_TIMEOUT = 10
    # MAX_CONCURRENT_REQUESTS = 5

    class Config:
        env_file = ".env"

settings = Settings()