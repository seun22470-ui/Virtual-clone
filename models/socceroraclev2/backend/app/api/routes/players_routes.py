import json
from typing import Union

from fastapi import APIRouter, Body, HTTPException
from pydantic import ValidationError
from app.schemas.player_schema import (
    PlayerSchema, 
    PlayerSeasonStatsSchema, 
    PlayerRecentMatchesSchema,
    PlayerSimilarityRequestSchema,
    PlayerSimilarityResponseSchema,
    SimilarPlayerSchema
)
from app.services.data_fetch.id_fetcher import get_player_id, get_league_id
from app.services.data_process.player_cleaner import player_season_stats, player_recent_matches
from app.models.db.embedding_model import find_similar_players

players_router = APIRouter()

@players_router.post("/player_id")
def get_player(request: PlayerSchema):
    result = get_player_id(request.player_name, request.team_name, request.league_name, request.country, request.season)

    if not result:
        return {"error": "Player not found."}

    player_id, player_name, position = result
    return {
        "player_id": player_id,
        "player_name": player_name,
        "position": position,
    }

@players_router.post("/player_season_stats")
def get_player_season_stats(request: PlayerSeasonStatsSchema):
    result = player_season_stats(request.player_name, request.team_name, request.league_name, request.season, request.country)

    if not result:
        return {"error": "Player season stats not found."}

    return result

@players_router.post("/player_recent_matches")
def get_player_recent_matches(request: PlayerRecentMatchesSchema):
    result = player_recent_matches(request.player_name, request.team_name, request.league_name, request.number_of_matches, request.season, request.country)

    if not result:
        return {"error": "Player recent matches not found."}

    return result

@players_router.post("/similar", response_model=PlayerSimilarityResponseSchema)
def find_similar_players_endpoint(request: PlayerSimilarityRequestSchema):
    """
    Find players similar to the given player based on their playing style embeddings.
    
    Returns a list of similar players with similarity scores (0-1, where 1 = identical).
    """
    # First, get the player ID from the name
    player_result = get_player_id(
        request.player_name, 
        request.team_name, 
        request.league_name, 
        request.country, 
        request.season
    )
    
    if not player_result:
        raise HTTPException(status_code=404, detail="Player not found.")
    
    player_id, player_name, position = player_result
    
    # Find similar players
    similar_players = find_similar_players(
        player_id=player_id,
        limit=request.limit,
        exclude_self=True,
        position_filter=request.position_filter,
        min_similarity=request.min_similarity
    )
    
    if not similar_players:
        return {
            "query_player": {
                "id": player_id,
                "player_name": player_name,
                "position": position
            },
            "similar_players": []
        }
    
    # Format response
    return {
        "query_player": {
            "id": player_id,
            "player_name": player_name,
            "position": position
        },
        "similar_players": similar_players
    }