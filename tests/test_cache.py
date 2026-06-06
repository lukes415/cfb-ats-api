from datetime import date, timedelta


def test_monday_cache_key_returns_monday():
    """Cache key should always be the Monday of the current week."""
    from services.cfbd_service import _monday_cache_key
    key = _monday_cache_key()
    d = date.fromisoformat(key)
    assert d.weekday() == 0, f"Expected Monday (weekday 0), got weekday {d.weekday()}"


def test_game_cache_needs_refresh_when_stale():
    """An entry cached 4 days ago should always trigger a refresh."""
    from datetime import datetime, timezone, timedelta
    from services.cfbd_service import _game_cache_needs_refresh

    cached_at = (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
    game_date = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()

    assert _game_cache_needs_refresh({"cached_at": cached_at, "game_date": game_date})


def test_game_cache_needs_refresh_when_game_imminent():
    """An entry cached today but with a game tomorrow should trigger a refresh."""
    from datetime import datetime, timezone, timedelta
    from services.cfbd_service import _game_cache_needs_refresh

    cached_at = datetime.now(timezone.utc).isoformat()
    game_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    assert _game_cache_needs_refresh({"cached_at": cached_at, "game_date": game_date})


def test_game_cache_does_not_refresh_when_fresh_and_far():
    """A recent entry for a game 2+ weeks out should be served from cache."""
    from datetime import datetime, timezone, timedelta
    from services.cfbd_service import _game_cache_needs_refresh

    cached_at = datetime.now(timezone.utc).isoformat()
    game_date = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()

    assert not _game_cache_needs_refresh({"cached_at": cached_at, "game_date": game_date})
