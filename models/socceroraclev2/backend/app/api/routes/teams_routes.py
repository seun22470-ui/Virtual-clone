from fastapi import APIRouter
from app.schemas.team_schema import TeamSchema, H2HStatsSchema, RecentMatchesSchema
from app.services.data_fetch.id_fetcher import get_team_id
from app.services.data_process.team_cleaner import H2H_stats, latest_H2H_stats, recent_matches

teams_router = APIRouter()

@teams_router.post("/team_id")
def get_team(request: TeamSchema):
    result = get_team_id(request.team_name, request.league_name, request.country, request.season)

    if not result:
        return {"error": "Team not found."}

    return result

@teams_router.post("/H2H_stats")
def get_H2H_stats(request: H2HStatsSchema):
    result = H2H_stats(request.team_1_name, request.team_2_name, request.league_name, request.country)

    if not result:
        return {"error": "H2H stats not found."}

    return result

@teams_router.post("/latest_H2H_stats")
def get_latest_H2H_stats(request: H2HStatsSchema):
    result = latest_H2H_stats(request.team_1_name, request.team_2_name, request.league_name, request.country)

    if not result:
        return {"error": "Latest H2H stats not found."}

    return result

@teams_router.post("/recent_matches")
def get_recent_matches(request: RecentMatchesSchema):
    result = recent_matches(request.team_name, request.league_name, request.number_of_matches, request.country)

    if not result:
        return {"error": "Recent matches not found."}

    return result