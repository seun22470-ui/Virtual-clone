import requests
from app.core.settings import api_key
from app.services.data_fetch.id_fetcher import get_season_year

headers = {
    'x-rapidapi-key': api_key,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def league_standings(league_name: str):
    """Fetch league standings for a single league and season."""
    url = "https://v3.football.api-sports.io/standings"

    leagues = {
        "premier-league": {"league": "39", "season": f"{get_season_year()}"},
        "la-liga": {"league": "140", "season": f"{get_season_year()}"},
        "serie-a": {"league": "135", "season": f"{get_season_year()}"},
        "bundesliga": {"league": "78", "season": f"{get_season_year()}"},
        "ligue-1": {"league": "61", "season": f"{get_season_year()}"},
    }

    league_name_clean = league_name.strip().lower().replace(" ", "-")
    if league_name_clean not in leagues:
        return {"error": f"Invalid league name: {league_name}"}

    params = leagues[league_name_clean]
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {"error": f"API request failed ({response.status_code})"}

    data = response.json()
    teams = data.get("response", [])

    if not teams:
        return {"league": league_name_clean, "standings": []}

    standings = teams[0]["league"]["standings"][0]

    league_data = [
        {
            "rank": team["rank"],
            "name": team["team"]["name"],
            "matches_played": team["all"]["played"],
            "wins": team["all"]["win"],
            "draws": team["all"]["draw"],
            "losses": team["all"]["lose"],
            "goals_for": team["all"]["goals"]["for"],
            "goals_against": team["all"]["goals"]["against"],
            "goal_diff": team["goalsDiff"],
            "points": team["points"],
            "last_five": team["form"],
            "standing": team.get("description", "Regular"),
        }
        for team in standings[:20]
    ]

    return {"league": league_name_clean, "standings": league_data}