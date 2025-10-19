import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CFBD_URL="https://api.collegefootballdata.com"
    CFBD_API_KEY = os.getenv("CFBD_API_KEY")

    API_TIMEOUT = 10
    MAX_CONCURRENT_REQUESTS = 5

settings = Settings()
