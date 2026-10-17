from fastapi import APIRouter
from app.schemas.league_schema import LeagueSchema
from app.services.data_fetch.id_fetcher import get_league_id
from app.services.data_fetch.league_standings import league_standings

standings_router = APIRouter()

@standings_router.post("/league_name")
def get_standings(request: LeagueSchema):
    league_id = get_league_id(request.league_name, request.country)

    if not league_id:
        return {"error": "League not found."}

    return {"league_id": league_id}

@standings_router.get("/standings/{league_name}")
def get_league_standings(league_name: str):
    """API endpoint to fetch standings for a single league."""
    data = league_standings(league_name)

    if "error" in data:
        return {"error": data["error"]}
    if not data.get("standings"):
        return {"error": "No standings found for this league."}

    return data