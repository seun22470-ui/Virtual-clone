from pydantic import BaseModel

class PlayerSchema(BaseModel):
    player_name: str
    team_name: str
    league_name: str
    season: int | None = None
    country: str | None = None

class PlayerSeasonStatsSchema(BaseModel):
    player_name: str
    team_name: str
    league_name: str
    season: int
    country: str | None = None

class PlayerRecentMatchesSchema(BaseModel):
    player_name: str
    team_name: str
    league_name: str
    number_of_matches: int
    season: int | None = None
    country: str | None = None

class PlayerSimilarityRequestSchema(BaseModel):
    player_name: str
    team_name: str
    league_name: str
    limit: int = 10
    position_filter: str | None = None
    min_similarity: float | None = None
    season: int | None = None
    country: str | None = None

class SimilarPlayerSchema(BaseModel):
    id: int
    player_name: str
    position: str
    similarity: float
    raw_data: dict

class PlayerSimilarityResponseSchema(BaseModel):
    query_player: dict
    similar_players: list[SimilarPlayerSchema]