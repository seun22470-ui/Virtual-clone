"""
Statistical normalization for player features.
Uses position-specific mean and standard deviation for z-score normalization.
"""
from typing import Dict, Optional
import numpy as np


# Position-specific normalization parameters (mean, std) based on research
# All values are per 90 minutes
POSITION_STATS = {
    'Defender': {
        'goals_total': {'mean': 0.05, 'std': 0.10},
        'goals_assists': {'mean': 0.05, 'std': 0.10},
        'goals_totalshots': {'mean': 0.5, 'std': 0.5},
        'goals_shotsongoal': {'mean': 0.2, 'std': 0.3},
        'passes_total': {'mean': 55, 'std': 15},
        'passes_key': {'mean': 0.5, 'std': 0.7},
        'passes_accuracy': {'mean': 84, 'std': 5},
        'tackles_total': {'mean': 2.0, 'std': 0.8},
        'tackles_blocks': {'mean': 0.6, 'std': 0.5},
        'tackles_interceptions': {'mean': 1.5, 'std': 0.7},
        'duels_total': {'mean': 9, 'std': 3},
        'duels_won': {'mean': 5, 'std': 2},
        'dribbles_attempts': {'mean': 0.6, 'std': 0.6},
        'dribbles_success': {'mean': 0.4, 'std': 0.5},
        'fouls_drawn': {'mean': 0.6, 'std': 0.5},
        'fouls_committed': {'mean': 1.0, 'std': 0.5},
        'cards_yellow': {'mean': 0.15, 'std': 0.15},
        'cards_red': {'mean': 0.01, 'std': 0.03},
    },
    
    'Midfielder': {
        'goals_total': {'mean': 0.12, 'std': 0.15},
        'goals_assists': {'mean': 0.15, 'std': 0.18},
        'goals_totalshots': {'mean': 1.2, 'std': 0.8},
        'goals_shotsongoal': {'mean': 0.5, 'std': 0.4},
        'passes_total': {'mean': 60, 'std': 18},
        'passes_key': {'mean': 1.4, 'std': 1.0},
        'passes_accuracy': {'mean': 83, 'std': 5},
        'tackles_total': {'mean': 2.1, 'std': 0.9},
        'tackles_blocks': {'mean': 0.4, 'std': 0.4},
        'tackles_interceptions': {'mean': 1.3, 'std': 0.6},
        'duels_total': {'mean': 10, 'std': 3},
        'duels_won': {'mean': 5.5, 'std': 2},
        'dribbles_attempts': {'mean': 1.4, 'std': 0.9},
        'dribbles_success': {'mean': 0.9, 'std': 0.7},
        'fouls_drawn': {'mean': 1.0, 'std': 0.7},
        'fouls_committed': {'mean': 1.4, 'std': 0.6},
        'cards_yellow': {'mean': 0.18, 'std': 0.16},
        'cards_red': {'mean': 0.01, 'std': 0.03},
    },
    
    'Attacker': {
        'goals_total': {'mean': 0.40, 'std': 0.25},
        'goals_assists': {'mean': 0.20, 'std': 0.20},
        'goals_totalshots': {'mean': 2.8, 'std': 1.2},
        'goals_shotsongoal': {'mean': 1.2, 'std': 0.6},
        'passes_total': {'mean': 32, 'std': 10},
        'passes_key': {'mean': 1.6, 'std': 1.1},
        'passes_accuracy': {'mean': 78, 'std': 6},
        'tackles_total': {'mean': 0.6, 'std': 0.6},
        'tackles_blocks': {'mean': 0.2, 'std': 0.3},
        'tackles_interceptions': {'mean': 0.4, 'std': 0.4},
        'duels_total': {'mean': 11, 'std': 4},
        'duels_won': {'mean': 4.5, 'std': 2},
        'dribbles_attempts': {'mean': 3.0, 'std': 1.5},
        'dribbles_success': {'mean': 1.6, 'std': 1.0},
        'fouls_drawn': {'mean': 1.8, 'std': 0.9},
        'fouls_committed': {'mean': 0.8, 'std': 0.5},
        'cards_yellow': {'mean': 0.10, 'std': 0.12},
        'cards_red': {'mean': 0.01, 'std': 0.03},
    },
    
    'Goalkeeper': {
        'goals_conceded': {'mean': 1.2, 'std': 0.5},
        'goals_saves': {'mean': 3.3, 'std': 1.3},
        'passes_total': {'mean': 30, 'std': 10},
        'passes_key': {'mean': 0.1, 'std': 0.2},
        'passes_accuracy': {'mean': 74, 'std': 7},
        'tackles_total': {'mean': 0.3, 'std': 0.3},
        'tackles_blocks': {'mean': 0.1, 'std': 0.2},
        'tackles_interceptions': {'mean': 0.1, 'std': 0.2},
        'duels_total': {'mean': 1.2, 'std': 0.7},
        'duels_won': {'mean': 0.8, 'std': 0.6},
        'dribbles_attempts': {'mean': 0.1, 'std': 0.2},
        'dribbles_success': {'mean': 0.1, 'std': 0.2},
        'fouls_drawn': {'mean': 0.2, 'std': 0.3},
        'fouls_committed': {'mean': 0.2, 'std': 0.3},
        'cards_yellow': {'mean': 0.03, 'std': 0.07},
        'cards_red': {'mean': 0.005, 'std': 0.02},
    }
}


def normalize_stat(value: float, mean: float, std: float) -> float:
    """
    Apply z-score normalization to a single stat.
    
    z = (value - mean) / std
    
    Args:
        value: Raw stat value
        mean: Position-specific mean
        std: Position-specific standard deviation
        
    Returns:
        Normalized z-score
    """
    if std == 0:
        return 0.0
    return (value - mean) / std


def normalize_stats(weighted_stats: Dict, position: str) -> Dict:
    """
    Normalize all stats using position-specific z-scores.
    
    Args:
        weighted_stats: Dict of weighted per-90 stats
        position: Player position (Defender, Midfielder, Attacker, Goalkeeper)
        
    Returns:
        Dict of normalized (z-score) stats
    """
    # Normalize position string
    position = position.strip()
    
    # Get normalization parameters for this position
    if position not in POSITION_STATS:
        raise ValueError(f"Unknown position: {position}. Must be one of: {list(POSITION_STATS.keys())}")
    
    position_params = POSITION_STATS[position]
    normalized = {}
    
    # Normalize each stat
    for stat_name, stat_value in weighted_stats.items():
        # Skip stats not in normalization table (like minutes_played, appearances, rating)
        if stat_name not in position_params:
            # Keep these stats as-is (they're metadata, not features)
            if stat_name in ['minutes_played', 'appearances', 'rating']:
                normalized[stat_name] = stat_value
            continue
        
        params = position_params[stat_name]
        normalized[stat_name] = normalize_stat(
            value=stat_value,
            mean=params['mean'],
            std=params['std']
        )
    
    return normalized


def get_normalization_params(position: str) -> Dict:
    """
    Get the mean/std parameters for a position.
    
    Args:
        position: Player position
        
    Returns:
        Dict of normalization parameters
    """
    position = position.strip()
    if position not in POSITION_STATS:
        raise ValueError(f"Unknown position: {position}")
    return POSITION_STATS[position]


def denormalize_stat(z_score: float, mean: float, std: float) -> float:
    """
    Convert a z-score back to original scale.
    Useful for interpreting results.
    
    value = (z_score × std) + mean
    
    Args:
        z_score: Normalized z-score
        mean: Position-specific mean
        std: Position-specific standard deviation
        
    Returns:
        Original scale value
    """
    return (z_score * std) + mean


def denormalize_stats(normalized_stats: Dict, position: str) -> Dict:
    """
    Convert normalized stats back to original per-90 scale.
    
    Args:
        normalized_stats: Dict of z-score normalized stats
        position: Player position
        
    Returns:
        Dict of per-90 stats on original scale
    """
    position = position.strip()
    if position not in POSITION_STATS:
        raise ValueError(f"Unknown position: {position}")
    
    position_params = POSITION_STATS[position]
    denormalized = {}
    
    for stat_name, z_score in normalized_stats.items():
        if stat_name not in position_params:
            denormalized[stat_name] = z_score
            continue
        
        params = position_params[stat_name]
        denormalized[stat_name] = denormalize_stat(
            z_score=z_score,
            mean=params['mean'],
            std=params['std']
        )
    
    return denormalized