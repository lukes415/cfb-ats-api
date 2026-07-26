from scripts.generate_fbs_teams import build_fbs_teams


def test_build_fbs_teams_filters_to_fbs_classification():
    all_teams = [
        {"id": 1, "school": "Air Force", "mascot": "Falcons", "conference": "Mountain West",
         "classification": "fbs", "color": "#004a7b", "alternateColor": "#ffffff",
         "logos": ["http://a.espncdn.com/i/teamlogos/ncaa/500/1.png",
                   "http://a.espncdn.com/i/teamlogos/ncaa/500-dark/1.png"]},
        {"id": 2, "school": "Abilene Christian", "mascot": "Wildcats", "conference": "UAC",
         "classification": "fcs", "color": "#592d82", "alternateColor": "#b1b3b3",
         "logos": ["http://a.espncdn.com/i/teamlogos/ncaa/500/2.png"]},
    ]

    result = build_fbs_teams(all_teams)

    assert len(result) == 1
    assert result[0]["id"] == 1


def test_build_fbs_teams_maps_fields_and_upgrades_logo_scheme():
    all_teams = [
        {"id": 1, "school": "Air Force", "mascot": "Falcons", "conference": "Mountain West",
         "classification": "fbs", "color": "#004a7b", "alternateColor": "#ffffff",
         "logos": ["http://a.espncdn.com/i/teamlogos/ncaa/500/1.png",
                   "http://a.espncdn.com/i/teamlogos/ncaa/500-dark/1.png"]},
    ]

    result = build_fbs_teams(all_teams)

    assert result[0] == {
        "id": 1,
        "name": "Air Force Falcons",
        "conference": "Mountain West",
        "logoURL": "https://a.espncdn.com/i/teamlogos/ncaa/500/1.png",
        "altLogoURL": "https://a.espncdn.com/i/teamlogos/ncaa/500-dark/1.png",
        "color": "#004a7b",
        "alternateColor": "#ffffff",
    }


def test_build_fbs_teams_handles_missing_second_logo():
    all_teams = [
        {"id": 1, "school": "Test", "mascot": "Team", "conference": "Test Conf",
         "classification": "fbs", "color": "#000000", "alternateColor": "#ffffff",
         "logos": ["http://a.espncdn.com/i/teamlogos/ncaa/500/1.png"]},
    ]

    result = build_fbs_teams(all_teams)

    assert result[0]["logoURL"] == "https://a.espncdn.com/i/teamlogos/ncaa/500/1.png"
    assert result[0]["altLogoURL"] is None
