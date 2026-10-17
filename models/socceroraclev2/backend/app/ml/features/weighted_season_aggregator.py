"""
Multi-season weighted feature aggregator for player embeddings.
Fetches player stats across multiple seasons and applies time-based weighting.
"""
from typing import Dict, List, Optional, Tuple
from app.services.data_process.player_cleaner import player_season_stats


# Season weights (most recent = highest weight)
SEASON_WEIGHTS = {
    2025: 1.0,
    2024: 0.6,
    2023: 0.3,
    2022: 0.15
}

# Validation thresholds
MIN_MINUTES_TOTAL = 450
MIN_MINUTES_PER_GAME = 30


def validate_season_data(season_data: Dict) -> bool:
    """
    Validate if a season's data meets minimum requirements.
    
    Args:
        season_data: Season stats payload from player_season_stats()
        
    Returns:
        True if valid, False otherwise
    """
    if not season_data or 'error' in season_data:
        return False
    
    games = season_data.get('games', {})
    minutes_played = games.get('minutes_played', 0) or 0
    appearances = games.get('appearances', 0) or 0
    
    # Check minimum total minutes
    if minutes_played < MIN_MINUTES_TOTAL:
        return False
    
    # Check minimum minutes per game
    if appearances > 0:
        avg_minutes_per_game = minutes_played / appearances
        if avg_minutes_per_game < MIN_MINUTES_PER_GAME:
            return False
    else:
        return False
    
    return True


def calculate_per_90_stats(season_data: Dict) -> Dict:
    """
    Convert raw season stats to per-90 minute metrics.
    
    Args:
        season_data: Season stats payload
        
    Returns:
        Dict with per-90 normalized stats
    """
    games = season_data.get('games', {})
    minutes = games.get('minutes_played', 0) or 0
    
    if minutes == 0:
        return {}
    
    position = season_data.get('position', '')
    is_gk = position.lower() == 'goalkeeper'
    
    def per_90(value):
        """Normalize value to per 90 minutes."""
        if value is None:
            return 0.0
        return (value / minutes) * 90
    
    def convert_percentage(accuracy_value):
        """Convert percentage to float, handling strings and None."""
        if accuracy_value is None:
            return 0.0
        if isinstance(accuracy_value, (int, float)):
            return float(accuracy_value)
        try:
            # Handle strings like "84%" or "84"
            return float(str(accuracy_value).replace('%', ''))
        except (ValueError, TypeError):
            return 0.0
    
    # Common stats for all players
    passes = season_data.get('passes', {})
    tackles_data = season_data.get('tackles', {})
    duels = season_data.get('duels', {})
    dribbles = season_data.get('dribbles', {})
    fouls = season_data.get('fouls', {})
    cards = season_data.get('cards', {})
    
    per_90_stats = {
        'passes_total': per_90(passes.get('total', 0) or 0),
        'passes_key': per_90(passes.get('key', 0) or 0),
        'passes_accuracy': convert_percentage(passes.get('accuracy')),
        
        'tackles_total': per_90(tackles_data.get('total', 0) or 0),
        'tackles_blocks': per_90(tackles_data.get('blocks', 0) or 0),
        'tackles_interceptions': per_90(tackles_data.get('interceptions', 0) or 0),
        
        'duels_total': per_90(duels.get('total', 0) or 0),
        'duels_won': per_90(duels.get('won', 0) or 0),
        
        'dribbles_attempts': per_90(dribbles.get('attempts', 0) or 0),
        'dribbles_success': per_90(dribbles.get('success', 0) or 0),
        
        'fouls_drawn': per_90(fouls.get('drawn', 0) or 0),
        'fouls_committed': per_90(fouls.get('committed', 0) or 0),
        
        'cards_yellow': per_90(cards.get('yellow', 0) or 0),
        'cards_red': per_90(cards.get('red', 0) or 0),
        
        'rating': season_data.get('rating', 0) or 0,
        'minutes_played': minutes,
        'appearances': games.get('appearances', 0) or 0
    }
    
    # Position-specific stats
    goals_data = season_data.get('goals', {})
    
    if is_gk:
        per_90_stats.update({
            'goals_conceded': per_90(goals_data.get('conceded', 0) or 0),
            'goals_saves': per_90(goals_data.get('saves', 0) or 0),
        })
    else:
        per_90_stats.update({
            'goals_total': per_90(goals_data.get('total', 0) or 0),
            'goals_assists': per_90(goals_data.get('assists', 0) or 0),
            'goals_totalshots': per_90(goals_data.get('totalshots', 0) or 0),
            'goals_shotsongoal': per_90(goals_data.get('shotsongoal', 0) or 0),
        })
    
    return per_90_stats


def redistribute_weights(valid_seasons: List[int]) -> Dict[int, float]:
    """
    Redistribute weights when seasons are missing.
    Missing weights are distributed proportionally across valid seasons.
    Total weight always sums to 2.05 (sum of all base weights).
    
    Args:
        valid_seasons: List of season years that have valid data
        
    Returns:
        Dict mapping season year to adjusted weight
    """
    if not valid_seasons:
        return {}
    
    # Calculate total missing weight
    all_seasons = [2025, 2024, 2023, 2022]
    missing_weight = sum(SEASON_WEIGHTS[s] for s in all_seasons if s not in valid_seasons)
    
    # Start with base weights for valid seasons
    adjusted_weights = {s: SEASON_WEIGHTS[s] for s in valid_seasons}
    
    # If there's missing weight, distribute proportionally
    if missing_weight > 0:
        # Calculate total base weight of valid seasons
        total_valid_weight = sum(SEASON_WEIGHTS[s] for s in valid_seasons)
        
        # Distribute missing weight proportionally based on each season's base weight
        for season in valid_seasons:
            proportion = SEASON_WEIGHTS[season] / total_valid_weight
            adjusted_weights[season] += missing_weight * proportion
    
    return adjusted_weights


def apply_weighted_average(seasons_data: Dict[int, Dict]) -> Dict:
    """
    Apply time-based weighting to multi-season per-90 stats.
    
    Args:
        seasons_data: Dict mapping season year to per-90 stats
        
    Returns:
        Dict with weighted average stats
    """
    if not seasons_data:
        return {}
    
    # Get adjusted weights
    valid_seasons = list(seasons_data.keys())
    weights = redistribute_weights(valid_seasons)
    
    # Calculate total weight for normalization
    total_weight = sum(weights.values())
    
    # Initialize weighted stats
    weighted_stats = {}
    
    # Get all stat keys from first valid season
    first_season = seasons_data[valid_seasons[0]]
    stat_keys = first_season.keys()
    
    # Calculate weighted average for each stat
    for stat_key in stat_keys:
        weighted_sum = 0.0
        
        for season, weight in weights.items():
            stat_value = seasons_data[season].get(stat_key, 0) or 0
            weighted_sum += stat_value * weight
        
        # Divide by total weight to get true weighted average
        weighted_stats[stat_key] = weighted_sum / total_weight
    
    return weighted_stats


def fetch_weighted_player_data(
    player_name: str,
    team_name: str,
    league_name: str,
    country: Optional[str] = None,
    seasons: Optional[List[int]] = None
) -> Optional[Dict]:
    """
    Fetch multi-season player data and apply time-based weighting.
    
    Args:
        player_name: Player's name
        team_name: Team name
        league_name: League name
        country: Optional country name
        seasons: Optional list of seasons (defaults to [2025, 2024, 2023, 2022])
        
    Returns:
        Dict with weighted stats, or None if no valid seasons found
    """
    if seasons is None:
        seasons = [2025, 2024, 2023, 2022]
    
    valid_seasons_data = {}
    player_position = None
    
    # Fetch and validate each season
    for season in seasons:
        print(f"[INFO] Fetching {player_name} season {season}...")
        
        season_data = player_season_stats(
            player_name=player_name,
            team_name=team_name,
            league_name=league_name,
            season=season,
            country=country
        )
        
        if validate_season_data(season_data):
            print(f"[SUCCESS] Season {season} valid (minutes: {season_data['games']['minutes_played']})")
            
            # Calculate per-90 stats
            per_90_stats = calculate_per_90_stats(season_data)
            valid_seasons_data[season] = per_90_stats
            
            # Store player position from first valid season
            if player_position is None:
                player_position = season_data.get('position', 'Unknown')
        else:
            print(f"[SKIP] Season {season} invalid or missing")
    
    # Check if we have any valid seasons
    if not valid_seasons_data:
        print(f"[ERROR] No valid seasons found for {player_name}")
        return None
    
    print(f"[INFO] Valid seasons: {list(valid_seasons_data.keys())}")
    
    # Apply weighted averaging
    weighted_stats = apply_weighted_average(valid_seasons_data)
    
    # Get adjusted weights for logging
    weights = redistribute_weights(list(valid_seasons_data.keys()))
    print(f"[INFO] Applied weights: {weights}")
    
    return {
        'player_name': player_name,
        'position': player_position,
        'weighted_stats': weighted_stats,
        'valid_seasons': list(valid_seasons_data.keys()),
        'weights_used': weights
    }


def batch_fetch_weighted_players(
    players_list: List[Dict]
) -> List[Dict]:
    """
    Fetch weighted data for multiple players.
    
    Args:
        players_list: List of dicts with 'player_name', 'team_name', 'league_name', 'country'
        
    Returns:
        List of weighted player data dicts
    """
    results = []
    
    for i, player_info in enumerate(players_list):
        print(f"\n[{i+1}/{len(players_list)}] Processing {player_info['player_name']}...")
        
        weighted_data = fetch_weighted_player_data(
            player_name=player_info['player_name'],
            team_name=player_info['team_name'],
            league_name=player_info['league_name'],
            country=player_info.get('country')
        )
        
        if weighted_data:
            results.append(weighted_data)
    
    print(f"\n[COMPLETE] Successfully processed {len(results)}/{len(players_list)} players")
    return results