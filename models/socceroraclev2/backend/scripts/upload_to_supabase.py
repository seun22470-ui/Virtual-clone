"""
Script to upload player embeddings to Supabase.

Usage:
    python backend/scripts/upload_to_supabase.py

Input:
    backend/app/ml/data/embeddings_complete.json

Output:
    Data uploaded to Supabase player_embeddings table
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.embeddings.supabase_uploader import upload_to_supabase
from app.ml.embeddings.config import DATA_DIR
from app.core.settings import supabase_connection_uri


# Use connection URI from settings
SUPABASE_CONNECTION_URI = supabase_connection_uri

# File paths
EMBEDDINGS_FILE = DATA_DIR / "embeddings_complete.json"


def main():
    """Main execution function."""
    print("=" * 60)
    print("SUPABASE UPLOAD SCRIPT")
    print("=" * 60)
    
    # Check if embeddings file exists
    if not EMBEDDINGS_FILE.exists():
        print(f"\n❌ Error: Embeddings file not found: {EMBEDDINGS_FILE}")
        print("\nPlease run train_and_generate_embeddings.py first!")
        sys.exit(1)
    
    print(f"\n📍 Database: Supabase PostgreSQL")
    print(f"📂 Embeddings file: {EMBEDDINGS_FILE.name}")
    
    # Confirm before uploading
    print(f"\n⚠️  This will clear the existing player_embeddings table and upload new data.")
    response = input("Continue? (y/n): ")
    
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)
    
    # Upload to Supabase
    result = upload_to_supabase(
        embeddings_file=str(EMBEDDINGS_FILE),
        connection_uri=SUPABASE_CONNECTION_URI,
        clear_first=True,  # Clear table before upload
        batch_size=100     # Upload 100 players at a time
    )
    
    # Final summary
    print("\n✅ Upload process complete!")
    print(f"   Total: {result['total']}")
    print(f"   Successful: {result['successful']}")
    print(f"   Failed: {result['failed']}")


if __name__ == "__main__":
    main()
