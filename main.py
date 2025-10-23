from fastapi import FastAPI
from schemas import Team, GamePrediction, GameScore, Coach, Venue, Line, Weather
from routes import games, chat, coaches, teams, venues, lines
from config import START_TIME

app = FastAPI(title="CFB ATS API", version="0.0.1")

app.include_router(games.router, prefix="/v1")
app.include_router(chat.router, prefix="/v1")
app.include_router(coaches.router, prefix="/v1")
app.include_router(teams.router, prefix="/v1")
app.include_router(venues.router, prefix="/v1")
app.include_router(lines.router, prefix="/v1")


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
    return {"as_of": START_TIME}

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
