import requests
from app.core.settings import api_key
from app.services.data_fetch.id_fetcher import get_season_year, get_league_id, get_team_id, get_fixture_id

BASE_URL = "https://v3.football.api-sports.io"

headers = {
    'x-rapidapi-key': api_key,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def H2H_stats(team_1_name: str, team_2_name: str, league_name: str, country: str = None):
    team_1_id = get_team_id(team_1_name, league_name, country)
    team_2_id = get_team_id(team_2_name, league_name, country)

    url = f"{BASE_URL}/fixtures/headtohead"
    params = {
        "h2h": f"{team_1_id}-{team_2_id}",
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        return {"error_code": response.status_code, "message": "Error fetching data"}

    data = response.json()
    fixtures = data.get("response", [])

    stats = {
        "total_games": len(fixtures),
        "home_games": 0,
        "away_games": 0,
        "wins_team_1": 0,
        "wins_team_2": 0,
        "draws": 0
    }

    for match in fixtures:
        home_team = match["teams"]["home"]["id"]
        away_team = match["teams"]["away"]["id"]
        home_winner = match["teams"]["home"]["winner"]
        away_winner = match["teams"]["away"]["winner"]

        if home_team == team_1_id:
            stats["home_games"] += 1
            if home_winner:
                stats["wins_team_1"] += 1
            elif away_winner:
                stats["wins_team_2"] += 1
            else:
                stats["draws"] += 1
        elif away_team == team_1_id:
            stats["away_games"] += 1
            if away_winner:
                stats["wins_team_1"] += 1
            elif home_winner:
                stats["wins_team_2"] += 1
            else:
                stats["draws"] += 1

    return stats

def latest_H2H_stats(team_1_name: str, team_2_name: str, league_name: str, country: str = None):
    team_1_id = get_team_id(team_1_name, league_name, country)
    team_2_id = get_team_id(team_2_name, league_name, country)

    url = f"{BASE_URL}/fixtures/headtohead"
    params = {
        "h2h": f"{team_1_id}-{team_2_id}",
        "last": 1,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return {"error_code": response.status_code, "message": "Error fetching data"}

    data = response.json()
    fixtures = data.get("response", [])
    if not fixtures:
        return None
    
    latest_fixture = fixtures[0]
    latest_match = latest_fixture["fixture"]["id"]
    
    # Extract match date and team information
    match_date = latest_fixture["fixture"].get("date", "")
    home_team_name = latest_fixture["teams"]["home"].get("name", "")
    away_team_name = latest_fixture["teams"]["away"].get("name", "")
    
    # Extract score information
    goals = latest_fixture.get("goals", {})
    score = latest_fixture.get("score", {})
    
    score_info = {
        "home": goals.get("home"),
        "away": goals.get("away"),
        "halftime": score.get("halftime", {}),
        "fulltime": score.get("fulltime", {}),
    }

    url = f"{BASE_URL}/fixtures/statistics"
    params = {
        "fixture": latest_match,
    }

    stats_response = requests.get(url, headers=headers, params=params)
    if stats_response.status_code != 200:
        return {"error_code": stats_response.status_code, "message": "Error fetching data"}
    
    stats_data = stats_response.json()
    statistics = stats_data.get("response", [])
    if not statistics:
        return None
    
    # Process statistics to return both teams with their metrics
    result = {
        "date": match_date,
        "home_team": home_team_name,
        "away_team": away_team_name,
        "score": score_info,
    }
    
    for team_stats in statistics:
        team_info = team_stats.get("team", {})
        team_name = team_info.get("name", "")
        
        # Build metrics dictionary from statistics array
        metrics = {}
        for stat in team_stats.get("statistics", []):
            stat_type = stat.get("type", "")
            stat_value = stat.get("value", "")
            metrics[stat_type] = stat_value
        
        result[team_name] = metrics
    
    return result

def recent_matches(team_name: str, league_name: str, number_of_matches: int, country: str = None):
    team_id = get_team_id(team_name, league_name, country)
    if not team_id:
        return None

    fixtures = get_fixture_id(team_name, get_season_year(), league_name, number_of_matches, country)
    if not fixtures:
        return None
    
    matches = []

    stats_url = f"{BASE_URL}/fixtures/statistics"
    fixture_url = f"{BASE_URL}/fixtures"

    for fixture in fixtures:
        fixture_id = fixture["fixture_id"]
        
        # Fetch full fixture details to get score information
        fixture_params = {
            "id": fixture_id,
        }
        fixture_response = requests.get(fixture_url, headers=headers, params=fixture_params)
        
        # Extract score information from fixture details
        score_info = None
        home_team_name = fixture.get("home_team", "")
        away_team_name = fixture.get("away_team", "")
        
        if fixture_response.status_code == 200:
            fixture_data = fixture_response.json()
            fixture_details = fixture_data.get("response", [])
            if fixture_details:
                full_fixture = fixture_details[0]
                goals = full_fixture.get("goals", {})
                score = full_fixture.get("score", {})
                
                # Update team names from full fixture if available
                teams = full_fixture.get("teams", {})
                if teams:
                    home_team_name = teams.get("home", {}).get("name", home_team_name)
                    away_team_name = teams.get("away", {}).get("name", away_team_name)
                
                score_info = {
                    "home": goals.get("home"),
                    "away": goals.get("away"),
                    "halftime": score.get("halftime", {}),
                    "fulltime": score.get("fulltime", {}),
                }

        # Fetch statistics for this fixture
        stats_params = {
            "fixture": fixture_id,
        }

        stats_response = requests.get(stats_url, headers=headers, params=stats_params)
        if stats_response.status_code != 200:
            # If stats fail, still add match with basic info
            match_data = {
                "date": fixture.get("date", ""),
                "home_team": home_team_name,
                "away_team": away_team_name,
                "score": score_info,
            }
            matches.append(match_data)
            continue

        stats_data = stats_response.json()
        statistics = stats_data.get("response", [])
        
        # Find the team's statistics in the response (response is a list of team objects)
        team_metrics = {}
        if statistics:
            for team_stats in statistics:
                team_info = team_stats.get("team", {})
                if team_info.get("id") == team_id:
                    # Extract statistics for this team
                    for stat in team_stats.get("statistics", []):
                        stat_type = stat.get("type", "")
                        stat_value = stat.get("value", "")
                        team_metrics[stat_type] = stat_value
                    break
        
        # Build match data with all information
        match_data = {
            "date": fixture.get("date", ""),
            "home_team": home_team_name,
            "away_team": away_team_name,
            "score": score_info,
            team_name: team_metrics,
        }
        
        matches.append(match_data)

    return matches