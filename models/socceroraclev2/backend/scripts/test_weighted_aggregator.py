"""
Test script for weighted season aggregator.
Tests the multi-season weighted data fetching logic.
"""
import sys
sys.path.insert(0, '/Users/ragpatel/SoccerOracleV2/SoccerOracleV2/backend')

from app.ml.features.weighted_season_aggregator import (
    fetch_weighted_player_data,
    validate_season_data,
    redistribute_weights,
    calculate_per_90_stats
)


def test_weight_redistribution():
    """Test weight redistribution logic."""
    print("=== Testing Weight Redistribution ===\n")
    
    test_cases = [
        ([2025, 2024, 2023, 2022], "All seasons valid"),
        ([2025, 2024, 2023], "Missing 2022"),
        ([2025, 2024], "Missing 2022, 2023"),
        ([2025], "Only 2025"),
        ([2025, 2023], "Missing 2024, 2022"),
    ]
    
    for valid_seasons, description in test_cases:
        weights = redistribute_weights(valid_seasons)
        total_weight = sum(weights.values())
        print(f"{description}:")
        print(f"  Valid seasons: {valid_seasons}")
        print(f"  Weights: {weights}")
        print(f"  Total weight: {total_weight:.2f}")
        print()


def test_single_player():
    """Test fetching data for a single player."""
    print("\n=== Testing Single Player Fetch ===\n")
    
    # Test with a well-known player
    result = fetch_weighted_player_data(
        player_name="Mohamed Salah",
        team_name="Liverpool",
        league_name="Premier League",
        country="England"
    )
    
    if result:
        print("\n✅ Successfully fetched weighted data!")
        print(f"Player: {result['player_name']}")
        print(f"Position: {result['position']}")
        print(f"Valid Seasons: {result['valid_seasons']}")
        print(f"Weights Used: {result['weights_used']}")
        
        print("\nWeighted Stats (Goals & Assists):")
        ws = result['weighted_stats']
        if 'goals_total' in ws:
            print(f"  Goals/90: {ws.get('goals_total', 0):.3f}")
            print(f"  Assists/90: {ws.get('goals_assists', 0):.3f}")
            print(f"  Shots/90: {ws.get('goals_totalshots', 0):.3f}")
        
        print("\nWeighted Stats (Passing):")
        print(f"  Passes/90: {ws.get('passes_total', 0):.3f}")
        print(f"  Key Passes/90: {ws.get('passes_key', 0):.3f}")
        print(f"  Pass Accuracy: {ws.get('passes_accuracy', 0):.1f}%")
        
        print("\nWeighted Stats (Duels & Dribbles):")
        print(f"  Duels/90: {ws.get('duels_total', 0):.3f}")
        print(f"  Duels Won/90: {ws.get('duels_won', 0):.3f}")
        print(f"  Dribbles/90: {ws.get('dribbles_attempts', 0):.3f}")
        
        print("\nWeighted Stats (Defensive):")
        print(f"  Tackles/90: {ws.get('tackles_total', 0):.3f}")
        print(f"  Interceptions/90: {ws.get('tackles_interceptions', 0):.3f}")
        
    else:
        print("❌ Failed to fetch player data")


def test_validation_logic():
    """Test season validation logic."""
    print("\n=== Testing Validation Logic ===\n")
    
    # Test case 1: Valid season
    valid_season = {
        'games': {
            'minutes_played': 2700,
            'appearances': 38
        },
        'goals': {'total': 20},
        'position': 'Forward'
    }
    print(f"Valid season (2700 min, 38 apps): {validate_season_data(valid_season)}")
    
    # Test case 2: Too few total minutes
    low_minutes = {
        'games': {
            'minutes_played': 400,
            'appearances': 10
        }
    }
    print(f"Low minutes (400 min): {validate_season_data(low_minutes)}")
    
    # Test case 3: Low minutes per game
    low_mpg = {
        'games': {
            'minutes_played': 500,
            'appearances': 20  # 25 min per game
        }
    }
    print(f"Low min/game (500 min, 20 apps): {validate_season_data(low_mpg)}")
    
    # Test case 4: Error response
    error_response = {'error': 'Player not found'}
    print(f"Error response: {validate_season_data(error_response)}")


if __name__ == "__main__":
    print("🧪 Weighted Season Aggregator Test Suite\n")
    print("=" * 60)
    
    # Run tests
    test_weight_redistribution()
    test_validation_logic()
    
    # Uncomment to test with real API (requires API key and credits)
    # test_single_player()
    
    print("\n" + "=" * 60)
    print("✅ Tests complete!")
