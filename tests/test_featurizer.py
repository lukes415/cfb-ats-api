import pytest
from datetime import datetime, timezone

FAKE_GAMES = [
    {"id": "1", "homeId": 10, "awayId": 20, "startDate": "2025-09-06T19:00:00Z"},
    {"id": "2", "homeId": 10, "awayId": 30, "startDate": "2025-09-13T19:00:00Z"},
    {"id": "3", "homeId": 40, "awayId": 10, "startDate": "2025-09-20T19:00:00Z"},
]


def test_compute_rest_days_returns_days_since_last_game():
    from services.featurizer import _compute_rest_days
    game_date = datetime(2025, 9, 20, 19, 0, 0, tzinfo=timezone.utc)
    # Team 10's last game before Sept 20 was Sept 13 → 7 days rest
    rest = _compute_rest_days(FAKE_GAMES, team_id=10, game_date=game_date)
    assert rest == 7


def test_compute_rest_days_returns_7_for_week1():
    from services.featurizer import _compute_rest_days
    game_date = datetime(2025, 9, 6, 19, 0, 0, tzinfo=timezone.utc)
    # Team 10's first game of the season — no prior game, default to 7
    rest = _compute_rest_days(FAKE_GAMES, team_id=10, game_date=game_date)
    assert rest == 7


FAKE_GAMES_WITH_LINES = [
    {"id": "1", "homeId": 10, "awayId": 20, "startDate": "2025-09-06T19:00:00Z", "covered": 1},
    {"id": "2", "homeId": 10, "awayId": 30, "startDate": "2025-09-13T19:00:00Z", "covered": 0},
    {"id": "3", "homeId": 40, "awayId": 10, "startDate": "2025-09-20T19:00:00Z", "covered": 1},
    {"id": "4", "homeId": 10, "awayId": 50, "startDate": "2025-09-27T19:00:00Z", "covered": 1},
]


def test_compute_ats_form_counts_covers():
    from services.featurizer import _compute_ats_form
    game_date = datetime(2025, 10, 4, 19, 0, 0, tzinfo=timezone.utc)
    # Team 10 in games 1-4:
    #   game1: home, covered=1 → cover ✓
    #   game2: home, covered=0 → no cover ✗
    #   game3: away, covered=1 (home team 40 covered) → team 10 did NOT cover ✗
    #   game4: home, covered=1 → cover ✓
    # Last 4 → 2 covers
    form = _compute_ats_form(FAKE_GAMES_WITH_LINES, team_id=10, game_date=game_date, n=4)
    assert form == 2
