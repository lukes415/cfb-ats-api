from fastapi import FastAPI
from app.routes import health, games

app = FastAPI(title="CFB ATS API", version="0.1.0")
app.include_router(health.router)
app.include_router(games.router, prefix="/predict")
