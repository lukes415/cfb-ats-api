import json
from fastapi import APIRouter, Query
from typing import List
from services.cfbd_service import cfbd_service
from datetime import datetime, timezone
from dateutil import parser
from config import TEAMS_FILE

router = APIRouter(prefix="/teams", tags=["teams"])

@router.get("")
def teams(year: int | None = None):
    year_to_use = datetime.now().year if not year else year
    try:
        with open(TEAMS_FILE, "r") as f:
            data = json.load(f)
        return [t for t in data]
    except FileNotFoundError:
        print(f"Teams file not found, fetching from API")
        return cfbd_service.fetch_teams(year_to_use)

@router.get("/next-games")
async def get_next_games(team_ids: str = Query(...)):
    """Get next games for multiple teams"""
    ids = [int(id.strip()) for id in team_ids.split(',')]
    now = datetime.now(timezone.utc)
    curr_year = now.year
    # Get all current year games
    all_games = await cfbd_service.fetch_games_for_year(curr_year)
    
    games_dict = {}
    for team_id in ids:      
        # Find team's future games, use ID because of inconsistency in name
        team_future_games = []
        for g in all_games:
            if g.get('homeId') != team_id and g.get('awayId') != team_id:
                continue
            
            # Parse start_date and check if it's in the future
            start_date_str = g.get('startDate')
            if start_date_str:
                try:
                    game_date = parser.isoparse(start_date_str)
                    if game_date >= now:
                        team_future_games.append(g)
                except:
                    pass  # Skip games with bad date formats
        
        # Sort by date and take first
        if team_future_games:
            team_future_games.sort(key=lambda g: g.get('startDate', ''))
            next_game = team_future_games[0]
            game_id = str(next_game['id'])
            
            if game_id not in games_dict:
                games_dict[game_id] = {
                    "id": game_id,
                    "home_team": next_game['homeTeam'],
                    "away_team": next_game['awayTeam'],
                    "date": next_game.get('startDate', ''),
                    "venue": next_game.get('venue', 'TBD'),
                    "week": next_game.get('week', 0),
                    "season": curr_year
                }
    
    return {"games": list(games_dict.values())}