import psycopg2
from app.core.settings import supabase_connection_uri

# Read from Database
def get_league_by_name(league_name: str, country: str = None):
    try:
        conn = psycopg2.connect(supabase_connection_uri)
        cur = conn.cursor()
        if country:
            cur.execute("SELECT id, league_name, country FROM leagues WHERE league_name = %s AND country = %s;", (league_name, country))
        else:
            cur.execute("SELECT id, league_name, country FROM leagues WHERE league_name = %s;", (league_name,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        print(f"[WARNING] Database connection failed: {e}")
        print("[INFO] Continuing without database cache...")
        return None

# Write to Database
def insert_league(league_id: int, league_name: str, country: str):
    try:
        conn = psycopg2.connect(supabase_connection_uri)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO leagues (id, league_name, country)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """,
            (league_id, league_name, country),
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"[INFO] Cached league {league_name} ({country}) (ID: {league_id}) to database")
    except Exception as e:
        print(f"[WARNING] Database connection failed: {e}")
        print("[INFO] Continuing without database cache...")