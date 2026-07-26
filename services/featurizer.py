import json
import asyncio
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from dateutil import parser as dateparser

from config import TEAMS_FILE, VENUES_FILE
from services.cfbd_service import cfbd_service


def _tz_offset_hours(tz_name: str | None, at: datetime) -> int:
    """
    Convert a venue's IANA timezone name (e.g. "America/Chicago", as CFBD
    returns it) to a UTC offset in whole hours at the given datetime.

    Training data encoded time_change as small integer hour deltas, so we
    round here to match. Falls back to 0 (UTC) for missing/unknown zones.
    """
    if not tz_name:
        return 0
    if at.tzinfo is None:
        at = at.replace(tzinfo=timezone.utc)
    try:
        return round(at.astimezone(ZoneInfo(tz_name)).utcoffset().total_seconds() / 3600)
    except Exception:
        return 0

# Conference name (as CFBD returns it) → column name suffix used in training.
# This mapping must exactly match the feature engineering in the training notebook.
CONFERENCE_COLUMNS = {
    "ACC": "in_acc",
    "American Athletic": "in_aac",
    "Big 12": "in_big12",
    "Big Ten": "in_big10",
    "Conference USA": "in_cusa",
    "FBS Independents": "independent",
    "Mid-American": "in_mac",
    "Mountain West": "in_mwc",
    "Pac-12": "in_pac12",
    "SEC": "in_sec",
    "Sun Belt": "in_sunbelt",
}


def _compute_rest_days(all_games: list, team_id: int, game_date: datetime) -> int:
    """
    Find the most recent prior game for a team and return how many days of rest
    they had entering the current game.

    Defaults to 7 (a standard weekly schedule) when no prior game is found —
    this covers week 1 and teams whose prior games aren't in the dataset.
    """
    prior_dates = []
    for g in all_games:
        if g.get("homeId") != team_id and g.get("awayId") != team_id:
            continue
        start_str = g.get("startDate", "")
        if not start_str:
            continue
        try:
            gd = dateparser.isoparse(start_str)
            if gd.tzinfo is None:
                gd = gd.replace(tzinfo=timezone.utc)
            if gd < game_date:
                prior_dates.append(gd)
        except Exception:
            pass

    if not prior_dates:
        return 7
    return (game_date - max(prior_dates)).days


def _compute_ats_form(all_games: list, team_id: int, game_date: datetime, n: int = 4) -> int:
    """
    Count how many times a team covered the spread in their last n completed games
    entering the current game.

    "covered" in the dataset is from the home team's perspective (1 = home covered).
    When the team was the away team, they covered if covered == 0.
    """
    completed = []
    for g in all_games:
        is_home = g.get("homeId") == team_id
        is_away = g.get("awayId") == team_id
        if not (is_home or is_away):
            continue
        if g.get("covered") is None:
            continue
        start_str = g.get("startDate", "")
        if not start_str:
            continue
        try:
            gd = dateparser.isoparse(start_str)
            if gd.tzinfo is None:
                gd = gd.replace(tzinfo=timezone.utc)
            if gd < game_date:
                covered = int(g["covered"])
                team_covered = covered if is_home else (1 - covered)
                completed.append((gd, team_covered))
        except Exception:
            pass

    completed.sort(key=lambda x: x[0])
    last_n = completed[-n:]
    return sum(c for _, c in last_n)


def _compute_ats_season(all_games: list, team_id: int, game_date: datetime) -> tuple[int, int]:
    """
    Count ATS covers and total completed games for a team so far this season,
    entering the current game. `all_games` is already season-scoped by the
    caller (fetch_games_for_year), so no year filtering is needed here.

    Returns (covers, games_played).
    """
    covers = 0
    games_played = 0
    for g in all_games:
        is_home = g.get("homeId") == team_id
        is_away = g.get("awayId") == team_id
        if not (is_home or is_away):
            continue
        if g.get("covered") is None:
            continue
        start_str = g.get("startDate", "")
        if not start_str:
            continue
        try:
            gd = dateparser.isoparse(start_str)
            if gd.tzinfo is None:
                gd = gd.replace(tzinfo=timezone.utc)
            if gd < game_date:
                covered = int(g["covered"])
                games_played += 1
                covers += covered if is_home else (1 - covered)
        except Exception:
            pass

    return covers, games_played


def _get_coach_tenure(coaches: list, school: str, season: int) -> tuple[int, bool]:
    """
    Returns (tenure_years, is_interim) for the head coach at a given school in a given season.

    Tenure is the number of years the coach has been at that school, used to compute
    tenure_delta. More tenure generally means a more established system and staff.
    """
    for coach in coaches:
        for season_entry in coach.get("seasons", []):
            if season_entry.get("school") == school and season_entry.get("year") == season:
                school_seasons = [
                    s for s in coach.get("seasons", [])
                    if s.get("school") == school and s.get("year") <= season
                ]
                tenure = len(school_seasons)
                is_interim = coach.get("firstName", "").lower() == "interim" or False
                return tenure, is_interim
    return 1, False


async def build_feature_row(
    game_id: str,
    home_team_id: int,
    away_team_id: int,
    venue_id: int,
    game_date: datetime,
    week: int,
    season: int,
    neutral: bool,
    feature_columns: list[str],
) -> pd.DataFrame:
    """
    Assemble a single-row DataFrame of model features for an upcoming game.
    Column order matches feature_columns.json exactly — the Pipeline requires this.

    All underlying data comes from sources already cached in cfbd_service,
    so this adds minimal latency to the request.
    """
    with open(TEAMS_FILE) as f:
        all_teams = json.load(f)
    with open(VENUES_FILE) as f:
        all_venues = json.load(f)

    team_map = {t["id"]: t for t in all_teams}
    venue_map = {v["id"]: v for v in all_venues}

    home_team = team_map.get(home_team_id, {})
    away_team = team_map.get(away_team_id, {})
    game_venue = venue_map.get(venue_id, {})
    home_venue = venue_map.get(home_team.get("locationVenueId"), {})
    away_venue = venue_map.get(away_team.get("locationVenueId"), {})

    elo_data, coaches, all_games = await asyncio.gather(
        cfbd_service.fetch_elo_for_week(season, week),
        cfbd_service.fetch_coaches_for_year(season),
        cfbd_service.fetch_games_for_year(season),
    )

    # ELO lookup is name-keyed in the CFBD ELO endpoint
    home_name = home_team.get("school", "")
    away_name = away_team.get("school", "")
    home_elo = next((e["elo"] for e in elo_data if e.get("team") == home_name), 1500)
    away_elo = next((e["elo"] for e in elo_data if e.get("team") == away_name), 1500)

    home_tenure, home_interim = _get_coach_tenure(coaches, home_name, season)
    away_tenure, away_interim = _get_coach_tenure(coaches, away_name, season)
    tenure_delta = home_tenure - away_tenure

    # away_time_change: offset between game venue and away team's home venue.
    # home_time_change: only non-zero for neutral site games.
    game_tz = _tz_offset_hours(game_venue.get("timezone"), game_date)
    home_home_tz = _tz_offset_hours(home_venue.get("timezone"), game_date) if home_venue.get("timezone") else game_tz
    away_home_tz = _tz_offset_hours(away_venue.get("timezone"), game_date) if away_venue.get("timezone") else game_tz
    away_time_change = game_tz - away_home_tz
    home_time_change = (game_tz - home_home_tz) if neutral else 0

    home_rest = _compute_rest_days(all_games, home_team_id, game_date)
    away_rest = _compute_rest_days(all_games, away_team_id, game_date)
    rest_diff = home_rest - away_rest

    home_ats_last4 = _compute_ats_form(all_games, home_team_id, game_date, n=4)
    away_ats_last4 = _compute_ats_form(all_games, away_team_id, game_date, n=4)

    home_ats_season_covers, home_ats_season_games = _compute_ats_season(all_games, home_team_id, game_date)
    away_ats_season_covers, away_ats_season_games = _compute_ats_season(all_games, away_team_id, game_date)

    game_details = await cfbd_service.fetch_game_details(game_id, game_date.isoformat(), season)
    weather = game_details.get("weather", {})
    spread = game_details.get("lines", {}).get("spread")

    home_conf = home_team.get("conference", "")
    away_conf = away_team.get("conference", "")
    home_fcs = int(home_conf not in CONFERENCE_COLUMNS)
    away_fcs = int(away_conf not in CONFERENCE_COLUMNS)

    row = {
        "neutral": int(neutral),
        "conference_game": int(home_conf == away_conf and home_conf != ""),
        "home_time_change": home_time_change,
        "away_time_change": away_time_change,
        "home_coach_interim": int(home_interim),
        "away_coach_interim": int(away_interim),
        "tenure_delta": tenure_delta,
        "spread": spread,
        "home_favorite": int(spread < 0) if spread is not None else 0,
        "temperature": weather.get("temperature", 65),
        "dew_point": weather.get("dew_point", 50),
        "humidity": weather.get("humidity", 60),
        "precipitation": weather.get("precipitation", 0),
        "weather_condition": weather.get("weather_condition", 800),  # 800 = clear in CFBD codes
        "wind_dir": weather.get("wind_dir", 0),
        "atm_pressure": weather.get("atm_pressure", 1013),
        "home_pregame_elo": home_elo,
        "away_pregame_elo": away_elo,
        "rest_diff": rest_diff,
        "home_ats_last4": home_ats_last4,
        "away_ats_last4": away_ats_last4,
        "home_ats_season_covers": home_ats_season_covers,
        "home_ats_season_games": home_ats_season_games,
        "away_ats_season_covers": away_ats_season_covers,
        "away_ats_season_games": away_ats_season_games,
        "home_team_id": home_team_id,
        "away_team_id": away_team_id,
    }

    for prefix, conf, fcs_val in [("home", home_conf, home_fcs), ("away", away_conf, away_fcs)]:
        for conf_name, col_suffix in CONFERENCE_COLUMNS.items():
            row[f"{prefix}_{col_suffix}"] = int(conf == conf_name)
        row[f"{prefix}_fcs"] = fcs_val

    df = pd.DataFrame([row])
    return df[feature_columns]
