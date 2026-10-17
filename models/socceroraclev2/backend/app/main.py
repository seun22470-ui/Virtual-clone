from fastapi import FastAPI
from app.api.routes.standings_route import standings_router
from app.api.routes.teams_routes import teams_router
from app.api.routes.players_routes import players_router
from app.api.routes.predictions_routes import predictions_router

app = FastAPI(
    title="Football Stats API",
    description="API for football statistics including standings, team comparisons, and player stats",
    version="1.0.0"
)

app.include_router(standings_router)
app.include_router(teams_router)
app.include_router(players_router)
app.include_router(predictions_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Football Stats API"}