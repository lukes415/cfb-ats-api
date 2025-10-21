from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    cfbd_base_url: str = "https://api.collegefootballdata.com"
    cfbd_api_key: str
    openai_api_key: str
    # API_TIMEOUT = 10
    # MAX_CONCURRENT_REQUESTS = 5

    class Config:
        env_file = ".env"

settings = Settings()