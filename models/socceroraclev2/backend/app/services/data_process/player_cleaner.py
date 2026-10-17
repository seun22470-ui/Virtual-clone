import requests
from app.services.data_fetch.id_fetcher import get_league_id, get_team_id, get_player_id, get_fixture_id
from app.core.settings import api_key
from app.services.data_fetch.id_fetcher import get_season_year
from app.models.db.player_stats_model import (
    get_cached_player_season_stats,
    insert_player_season_stats_once,
    upsert_player_season_stats,
)

BASE_URL = "https://v3.football.api-sports.io"
headers = {
    'x-rapidapi-key': api_key,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def _format_rating(raw_rating):
    if raw_rating is None:
        return None

    try:
        return float(f"{float(raw_rating):.2f}")
    except (TypeError, ValueError):
        return None

def player_season_stats(player_name: str, team_name: str, league_name: str, season: int, country: str = None):
    is_current_season = season == get_season_year()

    league_id = get_league_id(league_name, country)
    if not league_id:
        return None

    player_id = get_player_id(player_name, team_name, league_name, country, season)
    if not player_id:
        return None
    
    player_position = player_id[2]

    url = f"{BASE_URL}/players"
    params = {
        "id": player_id[0],
        "season": season,
        "league": league_id,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return {
            "error": "Upstream API request failed.",
            "status_code": response.status_code,
            "detail": response.json().get("message")
            if response.headers.get("content-type") == "application/json"
            else response.text,
        }
    
    data = response.json()
    if data.get("errors"):
        return {
            "error": "Upstream API returned errors.",
            "detail": data["errors"],
        }

    if not data["response"]:
        return {
            "error": "No player statistics returned from API.",
            "parameters": params,
        }
    
    stats = data["response"][0]["statistics"][0]
    
    if player_position == "Goalkeeper":
        result_payload = {
            "name": player_name,
            "position": "Goalkeeper",
            "rating": _format_rating(stats["games"].get("rating")),
            "games": {
                "appearances": stats["games"]["appearences"],
                "minutes_played": stats["games"]["minutes"]
            },
            "goals": {
                "conceded": stats["goals"]["conceded"],
                "saves": stats["goals"]["saves"]
            },
            "passes": {
                "total": stats["passes"]["total"],
                "key": stats["passes"]["key"],
                "accuracy": _convert_percentage_to_float(stats["passes"]["accuracy"])
            },
            "tackles": {
                "total": stats["tackles"]["total"],
                "blocks": stats["tackles"]["blocks"],
                "interceptions": stats["tackles"]["interceptions"]
            },
            "duels": {
                "total": stats["duels"]["total"],
                "won": stats["duels"]["won"]
            },
            "dribbles": {
                "attempts": stats["dribbles"]["attempts"],
                "success": stats["dribbles"]["success"]
            },
            "fouls": {
                "drawn": stats["fouls"]["drawn"],
                "committed": stats["fouls"]["committed"]
            },
            "cards": {
                "yellow": stats["cards"]["yellow"],
                "red": stats["cards"]["red"]
            }
        }
    else:
        result_payload = {
            "name": player_name,
            "position": player_position,
            "rating": _format_rating(stats["games"].get("rating")),
            "games": {
                "appearances": stats["games"]["appearences"],
                "minutes_played": stats["games"]["minutes"]
            },
            "goals": {
                "total": stats["goals"]["total"],
                "assists": stats["goals"]["assists"],
                "totalshots": stats["shots"]["total"],
                "shotsongoal": stats["shots"]["on"]
            },
            "passes": {
                "total": stats["passes"]["total"],
                "key": stats["passes"]["key"],
                "accuracy": _convert_percentage_to_float(stats["passes"]["accuracy"])
            },
            "tackles": {
                "total": stats["tackles"]["total"],
                "blocks": stats["tackles"]["blocks"],
                "interceptions": stats["tackles"]["interceptions"]
            },
            "duels": {
                "total": stats["duels"]["total"],
                "won": stats["duels"]["won"]
            },
            "dribbles": {
                "attempts": stats["dribbles"]["attempts"],
                "success": stats["dribbles"]["success"]
            },
            "fouls": {
                "drawn": stats["fouls"]["drawn"],
                "committed": stats["fouls"]["committed"]
            },
            "cards": {
                "yellow": stats["cards"]["yellow"],
                "red": stats["cards"]["red"]
            }
        }

    if is_current_season:
        upsert_player_season_stats(
            player_id[0],
            player_name,
            player_position,
            season,
            result_payload,
        )
    else:
        insert_player_season_stats_once(
            player_id[0],
            player_name,
            player_position,
            season,
            result_payload,
        )

    return result_payload

def _convert_percentage_to_float(accuracy_str):
    """Convert percentage string like '68%' to float."""
    if accuracy_str is None:
        return 0
    if isinstance(accuracy_str, (int, float)):
        return float(accuracy_str)
    try:
        # Remove % and convert to float
        return float(str(accuracy_str).replace('%', ''))
    except (ValueError, TypeError):
        return 0

def _extract_match_stats(stats, position, minutes_played):
    """Extract and format match statistics from API response."""
    # Determine if goalkeeper from position string or games.position
    is_goalkeeper = position == "Goalkeeper" or stats.get("games", {}).get("position") == "G"
    
    if is_goalkeeper:
        match_stats = {
            "games": {
                "appearances": 1 if minutes_played > 0 else 0,
                "minutes_played": minutes_played
            },
            "goals": {
                "conceded": stats.get("goals", {}).get("conceded", 0) or 0,
                "saves": stats.get("goals", {}).get("saves", 0) or 0
            },
            "passes": {
                "total": stats.get("passes", {}).get("total", 0) or 0,
                "key": stats.get("passes", {}).get("key", 0) or 0,
                "accuracy": _convert_percentage_to_float(stats.get("passes", {}).get("accuracy", 0))
            },
            "tackles": {
                "total": stats.get("tackles", {}).get("total", 0) or 0,
                "blocks": stats.get("tackles", {}).get("blocks", 0) or 0,
                "interceptions": stats.get("tackles", {}).get("interceptions", 0) or 0
            },
            "duels": {
                "total": stats.get("duels", {}).get("total", 0) or 0,
                "won": stats.get("duels", {}).get("won", 0) or 0
            },
            "dribbles": {
                "attempts": stats.get("dribbles", {}).get("attempts", 0) or 0,
                "success": stats.get("dribbles", {}).get("success", 0) or 0
            },
            "fouls": {
                "drawn": stats.get("fouls", {}).get("drawn", 0) or 0,
                "committed": stats.get("fouls", {}).get("committed", 0) or 0
            },
            "cards": {
                "yellow": stats.get("cards", {}).get("yellow", 0) or 0,
                "red": stats.get("cards", {}).get("red", 0) or 0
            }
        }
    else:
        match_stats = {
            "games": {
                "appearances": 1 if minutes_played > 0 else 0,
                "minutes_played": minutes_played
            },
            "goals": {
                "total": stats.get("goals", {}).get("total", 0) or 0,
                "assists": stats.get("goals", {}).get("assists", 0) or 0,
                "totalshots": stats.get("shots", {}).get("total", 0) or 0,
                "shotsongoal": stats.get("shots", {}).get("on", 0) or 0
            },
            "passes": {
                "total": stats.get("passes", {}).get("total", 0) or 0,
                "key": stats.get("passes", {}).get("key", 0) or 0,
                "accuracy": _convert_percentage_to_float(stats.get("passes", {}).get("accuracy", 0))
            },
            "tackles": {
                "total": stats.get("tackles", {}).get("total", 0) or 0,
                "blocks": stats.get("tackles", {}).get("blocks", 0) or 0,
                "interceptions": stats.get("tackles", {}).get("interceptions", 0) or 0
            },
            "duels": {
                "total": stats.get("duels", {}).get("total", 0) or 0,
                "won": stats.get("duels", {}).get("won", 0) or 0
            },
            "dribbles": {
                "attempts": stats.get("dribbles", {}).get("attempts", 0) or 0,
                "success": stats.get("dribbles", {}).get("success", 0) or 0
            },
            "fouls": {
                "drawn": stats.get("fouls", {}).get("drawn", 0) or 0,
                "committed": stats.get("fouls", {}).get("committed", 0) or 0
            },
            "cards": {
                "yellow": stats.get("cards", {}).get("yellow", 0) or 0,
                "red": stats.get("cards", {}).get("red", 0) or 0
            }
        }
    
    return match_stats

def player_recent_matches(player_name: str, team_name: str, league_name: str, number_of_matches: int, season: int, country: str = None):
    league_id = get_league_id(league_name, country)
    if not league_id:
        return None

    team_id = get_team_id(team_name, league_name, country, season)
    if not team_id:
        return None

    player_result = get_player_id(player_name, team_name, league_name, country, season)
    if not player_result:
        return None
    
    player_id, player_name_api, position = player_result

    matches = get_fixture_id(team_name, season, league_name, number_of_matches, country)
    if not matches:
        return None
    
    stats_url = f"{BASE_URL}/fixtures/players"
    player_stats = []

    for match in matches:
        stats_params = {
            "fixture": match["fixture_id"],
            "team": team_id,
        }

        stats_response = requests.get(stats_url, headers=headers, params=stats_params)
        if stats_response.status_code != 200:
            continue

        stats_data = stats_response.json()
        if not stats_data or stats_data.get("errors"):
            continue
        
        # Extract player statistics from the API response
        response_data = stats_data.get("response", [])
        if not response_data:
            continue
        
        # Find the player in the response
        player_found = False
        for team_data in response_data:
            players = team_data.get("players", [])
            for player_entry in players:
                if player_entry.get("player", {}).get("id") == player_id:
                    statistics = player_entry.get("statistics", [])
                    if statistics:
                        stats = statistics[0]
                        minutes_played = stats.get("games", {}).get("minutes", 0) or 0
                        
                        # Use position from stats if available, otherwise use from player_data
                        stats_position = stats.get("games", {}).get("position")
                        if stats_position == "G":
                            player_position = "Goalkeeper"
                        else:
                            player_position = position or stats_position or "Unknown"
                        
                        match_stats = _extract_match_stats(stats, player_position, minutes_played)
                        
                        player_stats.append({
                            "fixture_id": match["fixture_id"],
                            "home_team": match["home_team"],
                            "away_team": match["away_team"],
                            "date": match["date"],
                            "stats": match_stats
                        })
                    player_found = True
                    break
            if player_found:
                break
        
    return player_stats if player_stats else None