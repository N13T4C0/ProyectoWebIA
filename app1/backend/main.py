from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import config
from .ai_client import ask_model

app = FastAPI(title="Recomendador musical")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["POST"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    tastes: str


@app.post("/api/recommend")
async def recommend(body: RecommendRequest):
    return await ask_model(body.tastes)