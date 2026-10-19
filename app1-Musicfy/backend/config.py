import os
from pathlib import Path
from dotenv import load_dotenv

# Carga variables desde backend/.env si existe
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "meta-llama/llama-3.3-70b-instruct")
GEMINI_URL = os.getenv("GEMINI_URL", "https://openrouter.ai/api/v1/chat/completions")

# CORS: orígenes permitidos separados por comas
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
ALLOWED_ORIGINS = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

# Parámetros y límites
MAX_CARACTERES = int(os.getenv("MAX_CARACTERES", "500"))
AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "25.0"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "600"))
