"""
Script to train PCA models and generate player embeddings.

Usage:
    python backend/scripts/train_and_generate_embeddings.py

Input:
    backend/app/ml/data/collected_features.json

Output:
    - backend/app/ml/models/pca_*.pkl (PCA models)
    - backend/app/ml/models/pca_*_metadata.json (metadata)
    - backend/app/ml/data/embeddings_complete.json (embeddings)
"""
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.embeddings.pca_trainer import train_pca_models
from app.ml.embeddings.embedding_generator import generate_embeddings
from app.ml.embeddings.config import COLLECTED_FEATURES_JSON, DATA_DIR


def main():
    """Main execution function."""
    print("=" * 60)
    print("PCA TRAINING & EMBEDDING GENERATION")
    print("=" * 60)
    
    # Check if input file exists
    if not COLLECTED_FEATURES_JSON.exists():
        print(f"\n❌ Error: Input file not found: {COLLECTED_FEATURES_JSON}")
        print("\nPlease run collect_player_features.py first!")
        sys.exit(1)
    
    # Load collected features
    print(f"\n📂 Loading data from: {COLLECTED_FEATURES_JSON.name}")
    with open(COLLECTED_FEATURES_JSON, 'r') as f:
        players_data = json.load(f)
    
    print(f"   Found {len(players_data)} players")
    
    # Show position distribution
    position_counts = {}
    for player in players_data:
        pos = player.get('position', 'Unknown')
        position_counts[pos] = position_counts.get(pos, 0) + 1
    
    print("\nPosition distribution:")
    for position, count in sorted(position_counts.items()):
        print(f"  - {position}s: {count}")
    
    # STEP 2A: Train PCA models
    print("\nStarting PCA training...")
    training_results = train_pca_models(players_data)
    
    # STEP 2B: Generate embeddings
    print("\nGenerating embeddings...")
    enhanced_players = generate_embeddings(players_data)
    
    # Save embeddings to file
    output_file = DATA_DIR / "embeddings_complete.json"
    print(f"\n💾 Saving embeddings to: {output_file.name}")
    
    with open(output_file, 'w') as f:
        json.dump(enhanced_players, f, indent=2)
    
    print(f"   ✅ Saved {len(enhanced_players)} players with embeddings")
    
    # Summary
    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print(f"✅ PCA Models: {len(training_results['models_trained'])} trained")
    print(f"   Positions: {', '.join(training_results['models_trained'])}")
    print(f"\n✅ Embeddings: {len(enhanced_players)} generated")
    
    print("\n📁 Files created:")
    for position in training_results['models_trained']:
        print(f"   - pca_{position.lower()}.pkl")
        print(f"   - pca_{position.lower()}_metadata.json")
    print(f"   - embeddings_complete.json")
    
    print("\n✅ Next step: Run upload_to_supabase.py to push to database")


if __name__ == "__main__":
    main()
