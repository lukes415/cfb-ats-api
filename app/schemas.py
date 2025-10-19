from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

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

class Game(BaseModel):
    id: int = None
    season: int = None
    week: int = None
    venue: str = None
    venue_id: int = None
    home_team: str = None
    home_team_id: str = None
    home_conference: str = None
    home_points: int = None
    home_in_acc: int = None
    home_in_aac: int = None
    home_in_big12: int = None # Game
    home_in_big10: int = None # Game
    home_in_cusa: int = None # Game
    home_independent: int = None # Game
    home_in_mac: int = None # Game
    home_in_mwc: int = None # Game
    home_in_pac12: int = None # Game
    home_in_sec: int = None # Game
    home_in_sunbelt: int = None # Game
    home_fcs: int = None # Game
    home_time_change: int = None # Game
    away_team: str = None # Game
    away_team_id: int = None # Game
    away_conference: str = None #Game
    away_points: int = None # Game
    away_in_acc: int = None # Game
    away_in_aac: int = None # Game
    away_in_big12: int = None # Game
    away_in_big10: int = None # Game
    away_in_cusa: int = None # Game
    away_independent: int = None # Game
    away_in_mac: int = None # Game
    away_in_mwc: int = None # Game
    away_in_pac12: int = None # Game
    away_in_sec: int = None # Game
    away_in_sunbelt: int = None # Game
    away_fcs: int = None # Game
    start_date: datetime = None # Game
    home_pregame_elo: int = None # Game
    away_pregame_elo: int = None

class Coach(BaseModel):
    name: str = ""
    tenure: int = 0
    fired: bool = None
    interim: bool = False
    last_week_coached: int = None # Use if they were fired
    season: int = None
    season_games_coached: int = None # account for week 0 games and bye weeks

class Venue(BaseModel):
    id: int = -1
    name: str = None
    city: str = None
    state: str = None
    zip: str = None
    timezone: int = None

class BookLine(BaseModel):
    provider: str = ""
    spread: int = None
    formatted_spread: str = ""
    spread_open: int = None
    over_under: int = None
    over_under_open: int = None
    home_moneyline: int = None
    away_moneyline: int = None

class Line(BaseModel):
    id: int = 0
    season: int = None
    season_type: str = None
    week: int = None
    start_date: datetime = datetime.now()
    home_team_id: int = None
    home_team: str = None
    home_conference: str = None
    home_classification: str = None
    home_score: int = None
    away_team_id: int = None
    away_team: str = None
    away_conference: str = None
    away_classification: str = None
    away_score: int = None
    lines: list[BookLine] = []

class Weather(BaseModel):
    id: int = 0
    season: int = None
    week: int = None
    season_type: str = None
    start_time: datetime = datetime.now()
    game_indoors: bool = None
    home_team: str = None
    home_conference: str = None
    away_team: str = None
    away_conference: str = None
    venue_id: int = None
    venue: str = None
    temperature: int = None
    dew_point: int = None
    humidity: int = None
    precipitation: int = None
    snowfall: int = None
    wind_direction: int = None
    wind_speed: int = None
    pressure: int = None
    weather_condition_code: int = None
    weather_condition: str = None
