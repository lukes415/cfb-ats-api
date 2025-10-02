from pydantic import BaseModel, HttpUrl
from typing import Optional

class Team(BaseModel):
    id: int
    name: str
    logoURL: HttpUrl = None
    altLogoURL: Optional[HttpUrl] = None
    conference: Optional[str] = None

class GamePrediction(BaseModel):
    game_id: int
    home_team_id: int
    away_team_id: int
    spread: float
    prob_cover: float
    model_pick: bool

class GameScore(BaseModel):
    game_id: int
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str
    quarter: int
    home_score: int
    away_score: int
    clock: str
    spread: int