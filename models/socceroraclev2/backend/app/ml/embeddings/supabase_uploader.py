"""
Supabase uploader for player embeddings.
Uploads generated embeddings to Supabase player_embeddings table.
"""
import json
from typing import List, Dict
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_batch


class SupabaseUploader:
    """Handles uploading player embeddings to Supabase."""
    
    def __init__(self, connection_uri: str):
        """
        Initialize PostgreSQL connection.
        
        Args:
            connection_uri: PostgreSQL connection URI
        """
        self.connection_uri = connection_uri
        self.conn = None
        self.table_name = "player_embeddings"
        self.successful_uploads = 0
        self.failed_uploads = []
    
    def connect(self):
        """Establish database connection."""
        self.conn = psycopg2.connect(self.connection_uri)
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def transform_for_database(self, player_data: Dict) -> Dict:
        """
        Transform player data to database row format.
        
        Args:
            player_data: Player data from embeddings_complete.json
            
        Returns:
            Dict formatted for database insertion
        """
        # Build raw_data JSONB column
        raw_data = player_data.get('raw_data', {})
        raw_data['team_name'] = player_data.get('team_name')
        raw_data['league_name'] = raw_data.get('league_name', 'Unknown')
        
        # Add PCA metadata if available
        if 'pca_metadata' in player_data:
            raw_data['pca_metadata'] = player_data['pca_metadata']
        
        # Get embeddings
        embedding_12d = player_data['embedding_12d']
        embedding_raw_17d = player_data['embedding_raw_17d']
        
        # Pad raw embeddings to 17D if needed (goalkeepers have 15 features)
        if len(embedding_raw_17d) < 17:
            embedding_raw_17d = embedding_raw_17d + [0.0] * (17 - len(embedding_raw_17d))
        
        # Pad PCA embeddings to 12D if needed (for small datasets with <12 players per position)
        if len(embedding_12d) < 12:
            embedding_12d = embedding_12d + [0.0] * (12 - len(embedding_12d))
        
        # Build database row
        db_row = {
            'id': player_data.get('id'),  # Use player ID from API
            'player_name': player_data['player_name'],
            'embedding': embedding_12d,  # 12D (or fewer for small datasets)
            'embedding_raw': embedding_raw_17d,  # 17D
            'raw_data': raw_data,  # JSONB
            'position': player_data['position'],
            'model_version': player_data.get('model_version', 'unknown')
        }
        
        return db_row
    
    def clear_table(self):
        """
        Delete all existing rows from player_embeddings table.
        Use this for fresh uploads during testing.
        """
        print(f"🗑️  Clearing existing data from {self.table_name}...")
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name}")
            self.conn.commit()
            cursor.close()
            print(f"   ✅ Table cleared")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not clear table: {e}")
            print(f"   Continuing with upload...")
            if self.conn:
                self.conn.rollback()
    
    def upload_batch(self, players_batch: List[Dict]) -> bool:
        """
        Upload a batch of players to Supabase.
        
        Args:
            players_batch: List of player database rows
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            # Prepare SQL insert statement with explicit ID and timestamps
            insert_sql = f"""
                INSERT INTO {self.table_name} 
                (id, player_name, embedding, embedding_raw, raw_data, position, model_version, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            # Prepare batch data
            batch_data = []
            for player in players_batch:
                batch_data.append((
                    player['id'],  # Player ID from API
                    player['player_name'],
                    player['embedding'],
                    player['embedding_raw'],
                    json.dumps(player['raw_data']),  # Convert dict to JSON string
                    player['position'],
                    player['model_version']
                ))
            
            # Execute batch insert
            execute_batch(cursor, insert_sql, batch_data)
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"   ❌ Batch upload failed: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def upload_players(self, players_data: List[Dict], batch_size: int = 100, clear_first: bool = True):
        """
        Upload all players to Supabase in batches.
        
        Args:
            players_data: List of player data from embeddings_complete.json
            batch_size: Number of players per batch (default 100)
            clear_first: Whether to clear table before uploading (default True)
        """
        print("\n" + "="*60)
        print("UPLOADING TO SUPABASE")
        print("="*60)
        
        # Connect to database
        print(f"\n🔌 Connecting to database...")
        self.connect()
        print(f"   ✅ Connected")
        
        # Clear table if requested
        if clear_first:
            self.clear_table()
        
        # Transform all players
        print(f"\n📦 Preparing {len(players_data)} players for upload...")
        db_rows = []
        for player_data in players_data:
            try:
                db_row = self.transform_for_database(player_data)
                db_rows.append(db_row)
            except Exception as e:
                print(f"   ⚠️  Failed to transform {player_data.get('player_name', 'Unknown')}: {e}")
                self.failed_uploads.append({
                    'player': player_data.get('player_name', 'Unknown'),
                    'error': str(e)
                })
        
        print(f"   ✅ Prepared {len(db_rows)} rows")
        
        # Upload in batches
        print(f"\n📤 Uploading in batches of {batch_size}...")
        total_batches = (len(db_rows) + batch_size - 1) // batch_size
        
        for i in range(0, len(db_rows), batch_size):
            batch = db_rows[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"\n[Batch {batch_num}/{total_batches}] Uploading {len(batch)} players...")
            
            if self.upload_batch(batch):
                self.successful_uploads += len(batch)
                print(f"   ✅ Batch uploaded successfully")
            else:
                # If batch fails, try individual uploads
                print(f"   ⚠️  Batch failed, trying individual uploads...")
                for player_row in batch:
                    try:
                        cursor = self.conn.cursor()
                        insert_sql = f"""
                            INSERT INTO {self.table_name} 
                            (id, player_name, embedding, embedding_raw, raw_data, position, model_version, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        """
                        cursor.execute(insert_sql, (
                            player_row['id'],  # Player ID from API
                            player_row['player_name'],
                            player_row['embedding'],
                            player_row['embedding_raw'],
                            json.dumps(player_row['raw_data']),
                            player_row['position'],
                            player_row['model_version']
                        ))
                        self.conn.commit()
                        cursor.close()
                        self.successful_uploads += 1
                        print(f"      ✅ {player_row['player_name']}")
                    except Exception as e:
                        print(f"      ❌ {player_row['player_name']}: {e}")
                        if self.conn:
                            self.conn.rollback()
                        self.failed_uploads.append({
                            'player': player_row['player_name'],
                            'error': str(e)
                        })
        
        # Close connection
        self.close()
        print(f"\n🔌 Database connection closed")
        
        # Generate summary
        self.print_summary(len(players_data))
    
    def print_summary(self, total_players: int):
        """Print upload summary report."""
        print("\n" + "="*60)
        print("UPLOAD COMPLETE!")
        print("="*60)
        print(f"Total Players: {total_players}")
        print(f"Successfully Uploaded: {self.successful_uploads}")
        print(f"Failed: {len(self.failed_uploads)}")
        
        if self.failed_uploads:
            print("\nFailed Players:")
            for failed in self.failed_uploads:
                print(f"  - {failed['player']}: {failed['error']}")
        
        print("="*60)


def upload_to_supabase(
    embeddings_file: str,
    connection_uri: str,
    clear_first: bool = True,
    batch_size: int = 100
) -> Dict:
    """
    Main function to upload embeddings to Supabase.
    
    Args:
        embeddings_file: Path to embeddings_complete.json
        connection_uri: PostgreSQL connection URI
        clear_first: Whether to clear table first (default True)
        batch_size: Batch size for uploads (default 100)
        
    Returns:
        Dict with upload statistics
    """
    # Load embeddings
    print(f"📂 Loading embeddings from: {embeddings_file}")
    with open(embeddings_file, 'r') as f:
        players_data = json.load(f)
    
    print(f"   Found {len(players_data)} players")
    
    # Upload to Supabase
    uploader = SupabaseUploader(connection_uri)
    uploader.upload_players(players_data, batch_size=batch_size, clear_first=clear_first)
    
    return {
        'total': len(players_data),
        'successful': uploader.successful_uploads,
        'failed': len(uploader.failed_uploads),
        'failed_details': uploader.failed_uploads
    }
