import json
from pprint import pprint

def load_cache():
    with open('cache.json', 'r') as f:
        return json.load(f)

def explore_games(year=2024):
    cache = load_cache()
    games = cache.get(f'games_{year}', [])
    
    print(f"\n=== Games {year} ===")
    print(f"Total games: {len(games)}")
    
    if games:
        print(f"\nFirst game structure:")
        pprint(games[0])
        
        # Show available fields
        print(f"\nAvailable fields:")
        print(list(games[0].keys()))
        
        # Find a specific team
        team = input("\nEnter team name to search (or press Enter to skip): ")
        if team:
            team_games = [g for g in games if 
                         team.lower() in str(g.get('homeTeam', '')).lower() or 
                         team.lower() in str(g.get('awayTeam', '')).lower()]
            print(f"\n{team} games found: {len(team_games)}")
            if team_games:
                pprint(team_games[0])

if __name__ == "__main__":
    explore_games()