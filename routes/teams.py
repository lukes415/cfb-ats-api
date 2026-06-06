import json
from fastapi import APIRouter, Query
from services.cfbd_service import cfbd_service
import services.model_loader as model_loader
from services.featurizer import build_feature_row
from datetime import datetime, timezone
from dateutil import parser
from config import TEAMS_FILE, VENUES_FILE
from schemas import NextGameResponse, NextGamesResponse, VenueDetail, WeatherDetail, LinesDetail, PredictionDetail

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


@router.get("/next-game", response_model=NextGamesResponse)
async def get_next_games(team_ids: str = Query(...)):
    """
    Returns the next upcoming game for each requested team, enriched with
    venue details, weather, the consensus spread, and an ML prediction.

    All enrichment data comes from CFBD endpoints that are already cached
    by cfbd_service, so the overhead per game is minimal. Predictions are
    omitted if the model file hasn't been loaded (model_loader.predictions_enabled
    is False) — the endpoint stays functional without a trained model.
    """
    ids = [int(id.strip()) for id in team_ids.split(',')]
    now = datetime.now(timezone.utc)
    curr_year = now.year

    all_games = await cfbd_service.fetch_games_for_year(curr_year)

    with open(VENUES_FILE) as f:
        all_venues = json.load(f)
    venue_map = {v["id"]: v for v in all_venues}

    with open(TEAMS_FILE) as f:
        all_teams = json.load(f)
    team_map = {t["id"]: t for t in all_teams}

    games_dict: dict[str, NextGameResponse] = {}

    for team_id in ids:
        team_future_games = []
        for g in all_games:
            if g.get('homeId') != team_id and g.get('awayId') != team_id:
                continue
            start_date_str = g.get('startDate')
            if start_date_str:
                try:
                    game_date = parser.isoparse(start_date_str)
                    if game_date >= now:
                        team_future_games.append(g)
                except Exception:
                    pass

        if not team_future_games:
            continue

        team_future_games.sort(key=lambda g: g.get('startDate', ''))
        next_game = team_future_games[0]
        game_id = str(next_game['id'])

        if game_id in games_dict:
            continue  # already enriched this game from a different team

        game_date = parser.isoparse(next_game['startDate'])
        week = next_game.get('week', 0)
        home_team_id = next_game.get('homeId')
        away_team_id = next_game.get('awayId')
        venue_id = next_game.get('venueId')
        neutral = next_game.get('neutralSite', False)

        # --- Venue ---
        venue_raw = venue_map.get(venue_id, {})
        # CFBD returns "grass" as a boolean (True = grass, False = turf).
        grass = venue_raw.get("grass")
        surface = "Grass" if grass is True else ("Turf" if grass is False else None)
        venue_detail = VenueDetail(
            name=venue_raw.get("name"),
            city=venue_raw.get("city"),
            state=venue_raw.get("state"),
            surface=surface,
        ) if venue_raw else None

        # --- Weather + Lines (from game-level cache) ---
        game_details = await cfbd_service.fetch_game_details(game_id, next_game['startDate'], curr_year)
        weather_raw = game_details.get("weather", {})
        lines_raw = game_details.get("lines", {})

        weather_detail = WeatherDetail(
            temperature=weather_raw.get("temperature"),
            conditions=weather_raw.get("conditions"),
            wind_mph=weather_raw.get("wind_mph"),
        ) if weather_raw else None

        lines_detail = LinesDetail(spread=lines_raw.get("spread")) if lines_raw else None

        # --- ML Prediction ---
        prediction_detail = None
        if model_loader.predictions_enabled and lines_raw.get("spread") is not None:
            # Spread is a required model input — skip prediction if we don't have a line yet.
            # Early-season or obscure games may not have lines until a few days before kickoff.
            try:
                feature_df = await build_feature_row(
                    game_id=game_id,
                    home_team_id=home_team_id,
                    away_team_id=away_team_id,
                    venue_id=venue_id,
                    game_date=game_date,
                    week=week,
                    season=curr_year,
                    neutral=neutral,
                    feature_columns=model_loader._feature_columns,
                )
                pick_team_id, prob, factors = model_loader.predict(
                    feature_df, home_team_id, away_team_id
                )
                prediction_detail = PredictionDetail(
                    model_pick_team_id=pick_team_id,
                    prob_cover=round(prob, 3),
                    top_factors=factors,
                )
            except Exception as e:
                # Don't let a prediction failure break the whole endpoint.
                # Log and continue — the game card still shows without a prediction.
                print(f"[teams] Prediction failed for game {game_id}: {e}")

        games_dict[game_id] = NextGameResponse(
            id=game_id,
            home_team=next_game['homeTeam'],
            home_team_id=home_team_id,
            away_team=next_game['awayTeam'],
            away_team_id=away_team_id,
            date=next_game.get('startDate', ''),
            week=week,
            season=curr_year,
            venue=venue_detail,
            weather=weather_detail,
            lines=lines_detail,
            prediction=prediction_detail,
        )

    return NextGamesResponse(
        games=list(games_dict.values()),
        teams_requested=len(ids),
        games_found=len(games_dict),
    )
