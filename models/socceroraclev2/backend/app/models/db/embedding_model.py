import psycopg2
from typing import List, Dict, Optional, Tuple

from app.core.settings import supabase_connection_uri


def get_player_embedding(player_id: int) -> Optional[Tuple]:
    """
    Retrieve a player's embedding from the database.
    
    Args:
        player_id: The player's ID
        
    Returns:
        Tuple of (embedding_vector, position, model_version) or None if not found
    """
    try:
        conn = psycopg2.connect(supabase_connection_uri)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT embedding, position, model_version
            FROM player_embeddings
            WHERE id = %s;
            """,
            (player_id,)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        return result
    except Exception as e:
        print(f"[WARNING] Database connection failed: {e}")
        print("[INFO] Continuing without database cache...")
        return None


def find_similar_players(
    player_id: int,
    limit: int = 10,
    exclude_self: bool = True,
    position_filter: Optional[str] = None,
    min_similarity: Optional[float] = None
) -> List[Dict]:
    """
    Find players similar to the given player using vector similarity search.
    
    Args:
        player_id: The ID of the player to find similar players for
        limit: Maximum number of similar players to return (default: 10)
        exclude_self: Whether to exclude the query player from results (default: True)
        position_filter: Optional position filter (Goalkeeper, Defender, Midfielder, Attacker)
        min_similarity: Optional minimum similarity score threshold (0-1, where 1 = identical)
        
    Returns:
        List of dictionaries with player info and similarity scores:
        [
            {
                'id': int,
                'player_name': str,
                'position': str,
                'similarity': float,
                'raw_data': dict
            },
            ...
        ]
    """
    try:
        # First, get the query player's embedding
        query_result = get_player_embedding(player_id)
        if not query_result:
            return []
        
        query_embedding, query_position, query_model_version = query_result
        
        # Convert embedding to proper format if needed
        # If it's already a string/list, use it; otherwise convert
        if isinstance(query_embedding, str):
            embedding_param = query_embedding
        else:
            # Convert list/array to string format for PostgreSQL vector
            embedding_param = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"
        
        # Build the SQL query
        where_clauses = ["model_version = %s"]
        params = [query_model_version]
        
        # Exclude self if requested
        if exclude_self:
            where_clauses.append("id != %s")
            params.append(player_id)
        
        # Position filter
        if position_filter:
            where_clauses.append("position = %s")
            params.append(position_filter)
        
        where_sql = " AND ".join(where_clauses)
        
        # Execute similarity search query
        conn = psycopg2.connect(supabase_connection_uri)
        cur = conn.cursor()
        
        # Build query with proper parameter order:
        # 1. embedding (for CTE similarity calculation)
        # 2. WHERE clause params (model_version, id, position)
        # 3. limit
        query = f"""
            WITH similarity_scores AS (
                SELECT 
                    id,
                    player_name,
                    position,
                    raw_data,
                    1 - (embedding <=> %s::vector) as similarity
                FROM player_embeddings
                WHERE {where_sql}
            )
            SELECT id, player_name, position, raw_data, similarity
            FROM similarity_scores
            {f"WHERE similarity >= {min_similarity}" if min_similarity is not None else ""}
            ORDER BY similarity DESC
            LIMIT %s;
        """
        
        # Parameter order: embedding first (for CTE), then WHERE params, then limit
        all_params = [embedding_param] + params + [limit]
        
        cur.execute(query, all_params)
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        # Format results
        similar_players = []
        for row in results:
            player_id_result, player_name, position, raw_data, similarity = row
            similar_players.append({
                'id': player_id_result,
                'player_name': player_name,
                'position': position,
                'similarity': round(float(similarity), 4),
                'raw_data': raw_data if raw_data else {}
            })
        
        return similar_players
        
    except Exception as e:
        print(f"[WARNING] Failed to find similar players: {e}")
        print("[INFO] Continuing without similarity search...")
        return []


def find_similar_by_vector(
    embedding_vector: List[float],
    model_version: str,
    limit: int = 10,
    position_filter: Optional[str] = None,
    min_similarity: Optional[float] = None
) -> List[Dict]:
    """
    Find players similar to a given embedding vector.
    
    Args:
        embedding_vector: The embedding vector to search for
        model_version: The model version to filter by
        limit: Maximum number of similar players to return (default: 10)
        position_filter: Optional position filter
        min_similarity: Optional minimum similarity score threshold
        
    Returns:
        List of dictionaries with player info and similarity scores
    """
    try:
        where_clauses = ["model_version = %s"]
        params = [model_version]
        
        if position_filter:
            where_clauses.append("position = %s")
            params.append(position_filter)
        
        where_sql = " AND ".join(where_clauses)
        
        # Convert embedding to proper format
        if isinstance(embedding_vector, str):
            embedding_param = embedding_vector
        else:
            embedding_param = "[" + ",".join(str(float(x)) for x in embedding_vector) + "]"
        
        conn = psycopg2.connect(supabase_connection_uri)
        cur = conn.cursor()
        
        # Use CTE to calculate similarity, then filter
        query = f"""
            WITH similarity_scores AS (
                SELECT 
                    id,
                    player_name,
                    position,
                    raw_data,
                    1 - (embedding <=> %s::vector) as similarity
                FROM player_embeddings
                WHERE {where_sql}
            )
            SELECT id, player_name, position, raw_data, similarity
            FROM similarity_scores
            {f"WHERE similarity >= {min_similarity}" if min_similarity is not None else ""}
            ORDER BY similarity DESC
            LIMIT %s;
        """
        
        # Parameter order: embedding first (for CTE), then WHERE params, then limit
        all_params = [embedding_param] + params + [limit]
        
        cur.execute(query, all_params)
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        similar_players = []
        for row in results:
            player_id, player_name, position, raw_data, similarity = row
            similar_players.append({
                'id': player_id,
                'player_name': player_name,
                'position': position,
                'similarity': round(float(similarity), 4),
                'raw_data': raw_data if raw_data else {}
            })
        
        return similar_players
        
    except Exception as e:
        print(f"[WARNING] Failed to find similar players by vector: {e}")
        print("[INFO] Continuing without similarity search...")
        return []
