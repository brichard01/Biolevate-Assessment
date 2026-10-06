import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://pokedex:pokedex@localhost:5432/pokedex"
)
EMBEDDINGS_URL = os.environ.get("EMBEDDINGS_URL", "http://localhost:8080")
FRONTEND_PORT = os.environ.get("FRONTEND_PORT", "5173")
