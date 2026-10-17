import psycopg2
from psycopg2.extras import Json

from app.core.settings import supabase_connection_uri


def get_cached_player_season_stats(player_id: int, season: int):
    """Fetch cached player season stats from the database."""
    try:
        conn = psycopg2.connect(supabase_connection_uri)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT stats_json
            FROM player_season_stats
            WHERE player_id = %s AND season = %s;
            """,
            (player_id, season),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return None

        return row[0]
    except Exception as exc:
        print(f"[WARNING] Database connection failed: {exc}")
        print("[INFO] Continuing without database cache...")
        return None


def _ensure_player_season_schema(cur):
    """Ensure schema supports multiple seasons per player."""
    cur.execute(
        """
        ALTER TABLE player_season_stats
        ADD COLUMN IF NOT EXISTS player_id BIGINT;
        """
    )
    cur.execute(
        """
        UPDATE player_season_stats
        SET player_id = id
        WHERE player_id IS NULL;
        """
    )
    cur.execute(
        """
        DROP INDEX IF EXISTS player_season_stats_player_id_season_idx;
        """
    )
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS player_season_stats_player_id_season_idx
        ON player_season_stats (player_id, season);
        """
    )
    cur.execute(
        """
        DO $$
        DECLARE
            default_exists BOOLEAN;
        BEGIN
            SELECT EXISTS(
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'player_season_stats'
                  AND column_name = 'id'
                  AND column_default LIKE 'nextval%'
            )
            INTO default_exists;

            IF NOT default_exists THEN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relkind = 'S'
                      AND c.relname = 'player_season_stats_id_seq'
                      AND n.nspname = 'public'
                ) THEN
                    EXECUTE 'CREATE SEQUENCE public.player_season_stats_id_seq';
                END IF;

                EXECUTE 'SELECT setval(''public.player_season_stats_id_seq'', COALESCE((SELECT MAX(id) FROM player_season_stats), 0))';
                EXECUTE 'ALTER TABLE player_season_stats ALTER COLUMN id SET DEFAULT nextval(''public.player_season_stats_id_seq'')';
            END IF;
        END
        $$;
        """
    )


def upsert_player_season_stats(
    player_id: int,
    player_name: str,
    position: str | None,
    season: int,
    stats_payload: dict,
):
    """
    Insert or update season stats for a player.

    Used for the current season, where stats should be refreshed frequently.
    """
    try:
        conn = psycopg2.connect(supabase_connection_uri)
        cur = conn.cursor()
        _ensure_player_season_schema(cur)
        cur.execute(
            """
            INSERT INTO player_season_stats (player_id, player_name, position, stats_json, season, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (player_id, season) DO UPDATE
            SET player_name = EXCLUDED.player_name,
                position = EXCLUDED.position,
                stats_json = EXCLUDED.stats_json,
                updated_at = NOW();
            """,
            (player_id, player_name, position, Json(stats_payload), season),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as exc:
        print(f"[WARNING] Failed to upsert player season stats: {exc}")
        print("[INFO] Continuing without database cache...")


def insert_player_season_stats_once(
    player_id: int,
    player_name: str,
    position: str | None,
    season: int,
    stats_payload: dict,
):
    """
    Insert historical season stats. Once inserted, these do not get updated.
    """
    try:
        conn = psycopg2.connect(supabase_connection_uri)
        cur = conn.cursor()
        _ensure_player_season_schema(cur)
        cur.execute(
            """
            INSERT INTO player_season_stats (player_id, player_name, position, stats_json, season, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (player_id, season) DO NOTHING;
            """,
            (player_id, player_name, position, Json(stats_payload), season),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as exc:
        print(f"[WARNING] Failed to insert player season stats: {exc}")
        print("[INFO] Continuing without database cache...")

