"""Regenerates reference_data/fbs_teams.json from reference_data/all_teams.json.

Trims the full CFBD team list down to FBS-classification schools and includes
each team's primary/alternate colors so the iOS app can use them for accent
styling. Run manually after all_teams.json is refreshed via fetch_teams().
"""
import json
from pathlib import Path

ALL_TEAMS_FILE = Path(__file__).resolve().parent.parent / "reference_data" / "all_teams.json"
FBS_TEAMS_FILE = Path(__file__).resolve().parent.parent / "reference_data" / "fbs_teams.json"


def build_fbs_teams(all_teams: list[dict]) -> list[dict]:
    fbs_teams = []
    for team in all_teams:
        if team.get("classification") != "fbs":
            continue
        logos = team.get("logos") or []
        fbs_teams.append({
            "id": team["id"],
            "name": f"{team['school']} {team['mascot']}",
            "conference": team.get("conference"),
            "logoURL": logos[0].replace("http://", "https://") if len(logos) > 0 else None,
            "altLogoURL": logos[1].replace("http://", "https://") if len(logos) > 1 else None,
            "color": team.get("color"),
            "alternateColor": team.get("alternateColor"),
        })
    return fbs_teams


def main():
    all_teams = json.loads(ALL_TEAMS_FILE.read_text())
    fbs_teams = build_fbs_teams(all_teams)
    FBS_TEAMS_FILE.write_text(json.dumps(fbs_teams, indent=2) + "\n")
    print(f"Wrote {len(fbs_teams)} FBS teams to {FBS_TEAMS_FILE}")


if __name__ == "__main__":
    main()
