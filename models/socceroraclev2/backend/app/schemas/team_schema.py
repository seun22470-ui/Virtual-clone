from pydantic import BaseModel

class TeamSchema(BaseModel):
    team_name: str
    league_name: str
    country: str | None = None
    season: int | None = None

class RecentMatchesSchema(BaseModel):
    team_name: str
    league_name: str
    country: str | None = None
    number_of_matches: int

class H2HStatsSchema(BaseModel):
    team_1_name: str
    team_2_name: str
    league_name: str
    country: str | None = None