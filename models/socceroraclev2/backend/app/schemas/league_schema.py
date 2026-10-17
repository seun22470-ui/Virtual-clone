from pydantic import BaseModel

class LeagueSchema(BaseModel):
    league_name: str
    country: str | None = None