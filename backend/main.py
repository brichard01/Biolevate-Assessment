import logging

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import query_database as dataquery
from config import DATABASE_URL, FRONTEND_PORT
import embeddings

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{FRONTEND_PORT}",
        f"http://127.0.0.1:{FRONTEND_PORT}",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=5)


# Error handling: the real error is loggeds, the client only gets a generic message
GENERIC_ERROR = "Something went wrong. Please try again later."


@app.exception_handler(embeddings.EmbeddingsUnavailable)
def embeddings_unavailable(request: Request, error: embeddings.EmbeddingsUnavailable):
    logger.error("Embeddings service error: %s", error)
    return JSONResponse(status_code=503, content={"detail": GENERIC_ERROR},)


@app.exception_handler(psycopg.OperationalError)
def database_unavailable(request: Request, error: psycopg.OperationalError):
    logger.error("Database unavailable: %s", error)
    return JSONResponse(status_code=503, content={"detail": GENERIC_ERROR})


@app.exception_handler(Exception)
def unexpected_error(request: Request, error: Exception):
    logger.exception("Unexpected error: %s", error)
    return JSONResponse(status_code=500, content={"detail": GENERIC_ERROR})


# For each category: its table, the columns returned for the preview,
# and the columns that can be filtered with <column>_min / <column>_max.
SEARCH_CATEGORIES = {
    "pokemon": {
        "table": "pokemon",
        "columns": [
            "id", "name", "types", "sprite_url", "hp", "attack", "defense",
            "special_attack", "special_defense", "speed",
        ],
        "filters": [
            "hp", "attack", "defense", "special_attack", "special_defense", "speed",
        ],
    },
    "move": {
        "table": "moves",
        "columns": [
            "id", "name", "type", "damage_class", "power", "accuracy", "pp",
            "priority", "effect_chance", "short_effect",
        ],
        "filters": ["power", "accuracy", "pp", "priority", "effect_chance"],
    },
    "ability": {
        "table": "abilities",
        "columns": ["id", "name", "short_effect"],
        "filters": [],
    },
}

MAX_QUERY_LENGTH = 100
SEARCH_MODES = ["name", "description"]


@app.get("/filters")
def get_filters():
    # Bounds of the search sliders, e.g. {"pokemon": {"min_hp": 10, "max_hp": 250, ...}}.
    with get_connection() as conn:
        pokemon_bounds = dataquery.pokemon_stat_bounds(conn)
        move_bounds = dataquery.move_stat_bounds(conn)

    return {"pokemon": pokemon_bounds, "move": move_bounds, "ability": {}}


@app.get("/types")
def get_types():
    with get_connection() as conn:
        return dataquery.all_types(conn)


@app.get("/search")
def search(
    category: str,
    request: Request,
    q: str = "",
    mode: str = "name",
    types: list[str] = Query([]),
):
    if category not in SEARCH_CATEGORIES:
        raise HTTPException(status_code=400, detail="Unknown category")

    if mode not in SEARCH_MODES:
        raise HTTPException(status_code=400, detail="Unknown search mode")

    if len(q) > MAX_QUERY_LENGTH:
        raise HTTPException(status_code=400, detail="Query is too long")

    config = SEARCH_CATEGORIES[category]

    minimums = {}
    maximums = {}

    for column in config["filters"]:
        for suffix, bounds in [("min", minimums), ("max", maximums)]:
            key = f"{column}_{suffix}"
            value = request.query_params.get(key)
            if value is None or value == "":
                continue

            try:
                bounds[column] = int(value)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"{key} must be a number")

    table, columns = config["table"], config["columns"]
    description_search = mode == "description" and q.strip() != ""

    if description_search:
        query_vector = embeddings.to_pgvector(embeddings.embed([q])[0])

    with get_connection() as conn:
        if description_search:
            results = dataquery.search_by_description(
                conn, table, columns, q, query_vector, minimums, maximums, types
            )
        else:
            results = dataquery.search_by_name(
                conn, table, columns, q, minimums, maximums, types
            )

    return {"results": results}


@app.get("/pokemon/{pokemon_id}")
def get_pokemon(pokemon_id: int):
    with get_connection() as conn:
        pokemon = dataquery.pokemon_by_id(conn, pokemon_id)

        if pokemon is None:
            raise HTTPException(status_code=404, detail="Pokemon not found")

        moves = dataquery.moves_by_pokemon_id(conn, pokemon_id)
        abilities = dataquery.abilities_by_pokemon_id(conn, pokemon_id)
        stat_bounds = dataquery.pokemon_stat_bounds(conn)

    pokemon["moves"] = moves
    pokemon["abilities"] = abilities
    pokemon["stat_bounds"] = stat_bounds
    return pokemon


@app.get("/move/{move_id}")
def get_move(move_id: int):
    with get_connection() as conn:
        move = dataquery.move_by_id(conn, move_id)

        if move is None:
            raise HTTPException(status_code=404, detail="Move not found")

        pokemon = dataquery.pokemon_by_move_id(conn, move_id)

    move["learned_by_pokemon"] = pokemon
    return move


@app.get("/ability/{ability_id}")
def get_ability(ability_id: int):
    with get_connection() as conn:
        ability = dataquery.ability_by_id(conn, ability_id)

        if ability is None:
            raise HTTPException(status_code=404, detail="Ability not found")

        pokemon = dataquery.pokemon_by_ability_id(conn, ability_id)

    ability["pokemon"] = pokemon
    return ability
