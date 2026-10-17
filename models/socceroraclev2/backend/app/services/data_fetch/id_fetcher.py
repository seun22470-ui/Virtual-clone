import requests
from app.core.settings import api_key
from fuzzywuzzy import process
from datetime import datetime
from app.models.db.league_model import get_league_by_name, insert_league
from app.models.db.team_model import get_team_by_name, insert_team
from app.models.db.player_model import get_player_by_name, insert_player

BASE_URL = "https://v3.football.api-sports.io"

headers = {
    'x-rapidapi-key': api_key,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def get_season_year():
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    if month >= 8:
        return year
    else:
        return year - 1

def get_league_id(league_name, country: str = None):
    """Fetch league ID for a specific league."""
    existing_league = get_league_by_name(league_name, country)
    if existing_league:
        return existing_league[0]

    url = f"{BASE_URL}/leagues"
    if country:
        params = {"name": league_name, "country": country}
    else:
        params = {"search": league_name}
    
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {"error_code": response.status_code, "message": response.json().get("message", "API error")}

    data = response.json().get("response", [])
    if not data:
        return {"errorCode": 404, "message": "No leagues found"}
    
    choices = [l["league"]["name"] for l in data]
    best_match, _ = process.extractOne(league_name, choices)
    league_info = next(l for l in data if l["league"]["name"] == best_match)

    league_id = league_info["league"]["id"]
    league_name_api = league_info["league"]["name"]
    league_country = league_info["country"]["name"]

    insert_league(league_id, league_name_api, league_country)

    return league_id

def get_team_id(team_name: str, league_name: str, country: str = None, season: int | None = None):
    """Fetch team ID for a given team name."""
    if not season:
        season = get_season_year()

    league_id = get_league_id(league_name, country)

    if not league_id:
        return None

    # Check database cache first
    existing_team = get_team_by_name(team_name, league_id)
    if existing_team:
        return existing_team[0]

    url = f"{BASE_URL}/teams"

    if country:
        params = {"league": league_id, "season": season, "country": country}
    else:
        params = {"league": league_id, "season": season}
    
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None

    data = response.json()
    all_teams = data.get("response", [])

    if not all_teams:
        return None

    team_names = [t["team"]["name"] for t in all_teams]
    
    # Use fuzzy matching to find the best match
    best_match, confidence = process.extractOne(team_name, team_names)
    
    if confidence < 60:
        return None
    
    # Find the matched team
    matched_team = next(t for t in all_teams if t["team"]["name"] == best_match)
    team_id = matched_team["team"]["id"]
    team_name_api = matched_team["team"]["name"]
    
    # Cache the team in database
    insert_team(team_id, team_name_api, league_id, league_name)
    
    print(f"[SUCCESS] Found team '{best_match}' → ID: {team_id}")
    return team_id

def get_player_id(player_name: str, team_name: str, league_name: str, country: str = None, season: int | None = None):
    """Fetch player ID for a given player name."""
    if not season:
        season = get_season_year()
        
    team_id = get_team_id(team_name, league_name, country, season)

    if not team_id:
        return None

    # Check database cache first
    existing_player = get_player_by_name(player_name)
    if existing_player:
        return existing_player[0], existing_player[1], existing_player[3]  # player_id, player_name, position

    url = f"{BASE_URL}/players/squads"
    params = {"team": team_id}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None

    data = response.json()
    players = data["response"][0]["players"]
    
    # Find closest matching player name
    player_names = [p["name"] for p in players]
    best_match, score = process.extractOne(player_name, player_names)
    
    if score < 60:  # Threshold for matching
        return None
    
    player_data = next(p for p in players if p["name"] == best_match)
    player_id = player_data["id"]
    player_name_api = player_data["name"]
    photo_url = player_data.get("photo", "")
    
    # Cache the player in database
    insert_player(player_id, player_name_api, photo_url, player_data.get("position"))
    
    print(f"[SUCCESS] Found player '{best_match}' → ID: {player_id}")
    return player_id, best_match, player_data["position"]

def get_fixture_id(team_name: str, season: int, league_name: str, number_of_fixtures: int, country: str = None):
    url = f"{BASE_URL}/fixtures"
    params = {
        "team": get_team_id(team_name, league_name, country, season),
        "season": season,
        "status": "FT",
        "last": number_of_fixtures,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    fixtures = data["response"]
    if not fixtures:
        return None

    simplified = [
        {
            "home_team": f["teams"]["home"]["name"],
            "away_team": f["teams"]["away"]["name"],
            "fixture_id": f["fixture"]["id"],
            "date": f["fixture"]["date"],
        }
        for f in fixtures
    ]

    return simplified