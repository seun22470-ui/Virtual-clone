"""
Script to collect player features from input list.

Usage:
    python backend/scripts/collect_player_features.py

Input:
    backend/app/ml/data/players_input.json

Output:
    - backend/app/ml/data/collected_features.csv
    - backend/app/ml/data/collected_features.json
    - backend/app/ml/data/collection_report.txt
"""
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.embeddings.data_collector import collect_player_features
from app.ml.embeddings.config import PLAYERS_INPUT_FILE


def main():
    """Main execution function."""
    print("=" * 60)
    print("PLAYER FEATURE COLLECTION SCRIPT")
    print("=" * 60)
    
    # Check if input file exists
    if not PLAYERS_INPUT_FILE.exists():
        print(f"\n❌ Error: Input file not found: {PLAYERS_INPUT_FILE}")
        print("\nPlease create a JSON file with the following format:")
        print("""
[
    {
        "player_name": "Mohamed Salah",
        "team_name": "Liverpool",
        "league_name": "Premier League",
        "country": "England"
    },
    {
        "player_name": "Kevin De Bruyne",
        "team_name": "Manchester City",
        "league_name": "Premier League",
        "country": "England"
    }
]
        """)
        sys.exit(1)
    
    # Load players list
    print(f"\n📂 Loading players from: {PLAYERS_INPUT_FILE}")
    with open(PLAYERS_INPUT_FILE, 'r') as f:
        players_list = json.load(f)
    
    print(f"   Found {len(players_list)} players to process")
    
    # Confirm before proceeding
    print(f"\n⚠️  This will make approximately {len(players_list) * 3} API calls")
    response = input("Continue? (y/n): ")
    
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)
    
    # Collect features
    result = collect_player_features(players_list)
    
    print("\n" + "=" * 60)
    print("COLLECTION COMPLETE!")
    print("=" * 60)
    print(f"✅ Successful: {len(result['successful_players'])}")
    print(f"❌ Failed: {len(result['failed_players'])}")
    print(f"🌐 API calls: {result['api_calls_made']}")
    print("\nPosition breakdown:")
    for position, count in result['position_counts'].items():
        print(f"  {position}: {count}")
    
    print("\n📁 Output files created:")
    print(f"  - collected_features.csv")
    print(f"  - collected_features.json")
    print(f"  - collection_report.txt")
    
    print("\n✅ Next step: Train PCA models using collected_features.json")


if __name__ == "__main__":
    main()
