"""
Position-specific importance weights for player statistics.
Applied AFTER z-score normalization to emphasize stats relevant to each position.
"""
from typing import Dict


# Features to exclude from final feature vector for PCA
# These are still calculated/processed but not included in embeddings
EXCLUDED_FEATURES = [
    'passes_accuracy',   # Excluded per user request
    'rating',            # Metadata - not a feature
    'minutes_played',    # Metadata - not a feature
    'appearances'        # Metadata - not a feature
]


# Position-specific importance weights
# Applied to normalized z-scores to emphasize position-relevant stats
# Higher weight = more important for that position

ATTACKER_WEIGHTS = {
    # Attacking output (critical)
    'goals_total': 2.0,
    'goals_assists': 1.5,
    'goals_totalshots': 1.3,
    'goals_shotsongoal': 1.4,
    
    # Chance creation (important)
    'passes_key': 1.2,
    'dribbles_success': 1.6,      # Beating defenders crucial
    'dribbles_attempts': 1.4,     # Willingness to attack
    
    # Passing (modern attackers link play)
    'passes_total': 1.0,          # Build-up involvement
    'passes_accuracy': 1.0,       # Retention matters
    
    # Defensive work (minimal)
    'tackles_total': 0.3,
    'tackles_interceptions': 0.2,
    'tackles_blocks': 0.2,
    
    # Duels/physicality
    'duels_total': 0.8,
    'duels_won': 0.9,
    'fouls_drawn': 0.7,
    'fouls_committed': 0.4,
    
    # Discipline
    'cards_yellow': 0.3,
    'cards_red': 0.5,
}

MIDFIELDER_WEIGHTS = {
    # Balanced attacking contribution
    'goals_total': 1.2,           # Goalscoring midfielders valuable
    'goals_assists': 1.3,
    'goals_totalshots': 0.9,
    'goals_shotsongoal': 1.0,
    
    # Passing (critical)
    'passes_total': 1.5,
    'passes_key': 1.4,
    'passes_accuracy': 1.3,
    
    # Ball progression
    'dribbles_success': 1.0,
    'dribbles_attempts': 1.2,     # Progressive carrying important
    
    # Defensive contribution
    'tackles_total': 1.6,
    'tackles_interceptions': 1.5,
    'tackles_blocks': 1.2,
    
    # Duels
    'duels_total': 1.4,
    'duels_won': 1.5,
    'fouls_drawn': 0.8,
    'fouls_committed': 0.9,
    
    # Discipline
    'cards_yellow': 0.7,
    'cards_red': 0.8,
}

DEFENDER_WEIGHTS = {
    # Attacking (minimal)
    'goals_total': 0.3,
    'goals_assists': 0.6,
    'goals_totalshots': 0.2,
    'goals_shotsongoal': 0.2,
    
    # Passing (important)
    'passes_total': 1.2,
    'passes_key': 0.7,
    'passes_accuracy': 1.4,
    
    # Ball carrying
    'dribbles_success': 0.5,
    'dribbles_attempts': 0.4,
    
    # Defensive actions (CRITICAL)
    'tackles_total': 2.0,
    'tackles_interceptions': 2.0,
    'tackles_blocks': 1.8,
    
    # Duels
    'duels_total': 1.7,
    'duels_won': 1.8,
    'fouls_drawn': 0.5,
    'fouls_committed': 1.0,
    
    # Discipline (avoiding cards crucial)
    'cards_yellow': 1.3,
    'cards_red': 1.2,
}

GOALKEEPER_WEIGHTS = {
    'goals_conceded': 2.0,
    'goals_saves': 1.8,
    
    'passes_total': 1.0,
    'passes_key': 0.3,
    'passes_accuracy': 1.2,
    
    'tackles_total': 0.8,
    'tackles_interceptions': 0.7,
    'tackles_blocks': 0.5,
    
    'duels_total': 1.0,
    'duels_won': 1.1,
    
    'dribbles_success': 0.2,
    'dribbles_attempts': 0.2,
    
    'fouls_drawn': 0.1,
    'fouls_committed': 0.8,
    'cards_yellow': 0.7,
    'cards_red': 1.5,
}


def get_position_weights(position: str) -> Dict[str, float]:
    """
    Get importance weights for a specific position.
    
    Args:
        position: Player position (Defender, Midfielder, Attacker, Goalkeeper)
        
    Returns:
        Dict mapping stat name to importance weight
    """
    position = position.strip()
    
    weights_map = {
        'Defender': DEFENDER_WEIGHTS,
        'Midfielder': MIDFIELDER_WEIGHTS,
        'Attacker': ATTACKER_WEIGHTS,
        'Goalkeeper': GOALKEEPER_WEIGHTS,
    }
    
    if position not in weights_map:
        raise ValueError(f"Unknown position: {position}. Must be one of: {list(weights_map.keys())}")
    
    return weights_map[position]


def apply_position_weights(normalized_stats: Dict, position: str) -> Dict:
    """
    Apply position-specific importance weights to normalized stats.
    
    This amplifies or de-emphasizes stats based on their relevance to the position.
    Applied AFTER z-score normalization.
    
    Args:
        normalized_stats: Dict of z-score normalized stats
        position: Player position
        
    Returns:
        Dict of weighted normalized stats
    """
    position = position.strip()
    weights = get_position_weights(position)
    
    weighted_stats = {}
    
    for stat_name, z_score in normalized_stats.items():
        # Skip metadata stats (not in weights table)
        if stat_name not in weights:
            # Keep metadata as-is
            if stat_name in ['minutes_played', 'appearances', 'rating']:
                weighted_stats[stat_name] = z_score
            continue
        
        # Apply position weight to z-score
        weight = weights[stat_name]
        weighted_stats[stat_name] = z_score * weight
    
    return weighted_stats


def get_stat_importance(stat_name: str, position: str) -> float:
    """
    Get the importance weight for a specific stat and position.
    
    Args:
        stat_name: Name of the stat
        position: Player position
        
    Returns:
        Importance weight (higher = more important)
    """
    weights = get_position_weights(position)
    return weights.get(stat_name, 0.0)


def compare_position_importance(stat_name: str) -> Dict[str, float]:
    """
    Compare how important a stat is across different positions.
    
    Args:
        stat_name: Name of the stat to compare
        
    Returns:
        Dict mapping position to importance weight
    """
    return {
        'Defender': DEFENDER_WEIGHTS.get(stat_name, 0.0),
        'Midfielder': MIDFIELDER_WEIGHTS.get(stat_name, 0.0),
        'Attacker': ATTACKER_WEIGHTS.get(stat_name, 0.0),
        'Goalkeeper': GOALKEEPER_WEIGHTS.get(stat_name, 0.0),
    }


def filter_excluded_features(stats_dict: Dict) -> Dict:
    """
    Remove excluded features from a stats dictionary.
    Used before converting to feature vector for PCA.
    
    Args:
        stats_dict: Dictionary of player stats
        
    Returns:
        Dictionary with excluded features removed
    """
    return {
        key: value 
        for key, value in stats_dict.items() 
        if key not in EXCLUDED_FEATURES
    }


def get_feature_names(position: str) -> list:
    """
    Get the list of feature names that will be included in the final vector.
    Excludes metadata and explicitly excluded features.
    
    Args:
        position: Player position
        
    Returns:
        List of feature names in order
    """
    weights = get_position_weights(position)
    return sorted([
        key for key in weights.keys() 
        if key not in EXCLUDED_FEATURES
    ])