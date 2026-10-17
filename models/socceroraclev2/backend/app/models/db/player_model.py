import psycopg2
from app.core.settings import supabase_connection_uri

# READ from Database
def get_player_by_name(player_name: str):
    """Retrieve a player by name."""
    try:
        conn = psycopg2.connect(supabase_connection_uri)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, player_name, photo_url, position
            FROM players 
            WHERE player_name = %s;
            """,
            (player_name,)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        print(f"[WARNING] Database connection failed: {e}")
        print("[INFO] Continuing without database cache...")
        return None

# WRITE to Database
def insert_player(player_id: int, player_name: str, photo_url: str, position: str | None = None):
    """Insert a player into the database (idempotent)."""
    try:
        conn = psycopg2.connect(supabase_connection_uri)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO players (id, player_name, photo_url, position)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET player_name = EXCLUDED.player_name,
                photo_url = EXCLUDED.photo_url,
                position = EXCLUDED.position;
            """,
            (player_id, player_name, photo_url, position)
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"[INFO] Player inserted: {player_name} ({player_id})")
    except Exception as e:
        print(f"[WARNING] Database connection failed: {e}")
        print("[INFO] Continuing without database cache...")

