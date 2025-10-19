from fastapi import FastAPI
from .schemas import Team, GamePrediction, GameScore, Coach, Venue, Line, Weather
import json
from pathlib import Path
from datetime import datetime
import httpx
import asyncio
from .config import settings

HEADERS = {
    "Authorization": f"Bearer {settings.CFBD_API_KEY}"
}

app = FastAPI(title="CFB ATS API", version="0.0.1")

TEAMS_FILE = Path("./reference_data") / "fbs_teams.json"

AS_OF = datetime.now()

SAMPLE_SCORE = GameScore(game_id=1, home_team_id=1, home_team_name="Georgia", away_team_id=2, away_team_name="Alabama", quarter=4, home_score=14, away_score=24, clock="15:00", spread=-4)
SAMPLE_PREDICITONS = [
        GamePrediction(game_id=1234, home_team_id=333, away_team_id=194,
                       spread=-7.5, prob_cover=0.62, model_pick=True),
        GamePrediction(game_id=5678, home_team_id=251, away_team_id=333,
                       spread=+3.0, prob_cover=0.41, model_pick=False),
    ]

@app.get("/health")
def health():
    return {"ok": True, "version": "0.0.1"}

@app.get("/live")
def live():
    return {"as_of": AS_OF}

@app.get("/teams", response_model=list[Team])
def teams():
    with open(TEAMS_FILE, "r") as f:
        data = json.load(f)
    return [Team(**t) for t in data]

async def fetch_games_for_year(year: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.CFBD_URL}/games?year={year}", headers=HEADERS)
            return response.json()
        except httpx.HTTPStatusError as e:
            # Flesh this out
            print("HTTP status error")
            print(e)
        except Exception as e:
            #Flesh this out
            print("general exception")
            print(e)

@app.get("/games")
async def games(start_year: int, end_year: int, home_fbs_only: bool | None = False):
    if end_year < start_year:
        return []
    years = range(start_year, end_year + 1)
    tasks = [fetch_games_for_year(year) for year in years]

    results = await asyncio.gather(*tasks)

    all_games = []
    for year_data in results:
        all_games.extend(year_data)
    # Add in game data massaging logic to map to Game class
    return all_games

@app.get("/coaches", response_model=list[Coach])
def coaches(start_year: int, end_year: int | None = None):
    return [Coach()]

@app.get("/venues", response_model=list[Venue])
def venues():
    return [Venue()]

@app.get("/lines", response_model=list[Line])
def lines(start_year: int, end_year: int):
    return [Line()]

@app.get("/weather", response_model=list[Weather])
def weather(start_year: int, end_year: int):
    return [Weather()]

@app.get("/score", response_model=list[GameScore])
def get_score(game_id: int):
    # mocked up
    return [SAMPLE_SCORE]

@app.get("/predict", response_model=list[GamePrediction])
def predict(season: int, week: int):
    # mocked up
    return SAMPLE_PREDICITONS
