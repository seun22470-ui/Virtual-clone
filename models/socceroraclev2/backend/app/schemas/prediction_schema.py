from pydantic import BaseModel

class PredictionRequest(BaseModel):
    team1: str
    team2: str
    league: str | None = None