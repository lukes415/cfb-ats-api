from fastapi import FastAPI, Query
from .schemas import Team, GamePrediction, GameScore
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(title="CFB ATS API (Mock)", version="0.0.1")

TEAMS_FILE = Path("./reference_data") / "fbs_teams.json"

AS_OF = datetime.now()

SAMPLE_SCORE = GameScore(game_id=1, home_team_id=1, home_team_name="Georgia", away_team_id=2, away_team_name="Alabama", quarter=4, home_score=14, away_score=24, clock="15:00", spread=-4)

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

@app.get("/score", response_model=list[GameScore])
def get_score(game_id: int = Query(...)):
    return [SAMPLE_SCORE]

@app.get("/predict", response_model=list[GamePrediction])
def predict(season: int = Query(...), week: int = Query(...)):
    # Mock output; wire real model later
    return [
        GamePrediction(game_id="2025-05-333-194", home_team_id=333, away_team_id=194,
                       spread=-7.5, prob_cover=0.62, model_pick=True),
        GamePrediction(game_id="2025-05-251-333", home_team_id=251, away_team_id=333,
                       spread=+3.0, prob_cover=0.41, model_pick=False),
    ]
