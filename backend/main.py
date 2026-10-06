import os

import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://pokedex:pokedex@localhost:5432/pokedex"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


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


# Minimum trigram similarity for a name to match the query (0 = anything, 1 = exact).
NAME_SIMILARITY_THRESHOLD = 0.3
MAX_QUERY_LENGTH = 100


@app.get("/search")
def search(category: str, request: Request, q: str = ""):
    if category not in SEARCH_CATEGORIES:
        raise HTTPException(status_code=400, detail="Unknown category")

    if len(q) > MAX_QUERY_LENGTH:
        raise HTTPException(status_code=400, detail="Query is too long")

    config = SEARCH_CATEGORIES[category]

    conditions = []
    values = {}

    for column in config["filters"]:
        for suffix, operator in [("min", ">="), ("max", "<=")]:
            key = f"{column}_{suffix}"
            value = request.query_params.get(key)
            if value is None or value == "":
                continue

            try:
                values[key] = int(value)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"{key} must be a number")

            conditions.append(
                sql.SQL("{} {} {}").format(
                    sql.Identifier(column), sql.SQL(operator), sql.Placeholder(key)
                )
            )

    # Fuzzy name search: names are compared without hyphens ("thunder-punch" -> "thunder punch").
    # word_similarity handles typos and partial names, starts_with ranks prefixes first.
    query_text = q.strip().lower().replace("-", " ")
    name = sql.SQL("replace(name, '-', ' ')")
    order_by = sql.SQL("id")

    if query_text:
        values["q"] = query_text
        values["threshold"] = NAME_SIMILARITY_THRESHOLD
        conditions.append(
            sql.SQL("word_similarity(%(q)s, {name}) >= %(threshold)s").format(name=name)
        )
        order_by = sql.SQL(
            "starts_with({name}, %(q)s) DESC, word_similarity(%(q)s, {name}) DESC, "
            "similarity(%(q)s, {name}) DESC, id"
        ).format(name=name)

    # Column and table names only come from SEARCH_CATEGORIES, values are passed as parameters.
    query = sql.SQL("SELECT {columns} FROM {table}").format(
        columns=sql.SQL(", ").join(sql.Identifier(c) for c in config["columns"]),
        table=sql.Identifier(config["table"]),
    )
    if conditions:
        query += sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions)
    query += sql.SQL(" ORDER BY ") + order_by

    with get_connection() as conn:
        results = conn.execute(query, values).fetchall()

    return {"results": results}


@app.get("/pokemon/{pokemon_id}")
def get_pokemon(pokemon_id: int):
    with get_connection() as conn:
        pokemon = conn.execute(
            """
            SELECT id, name, types, height_dm, weight_hg, base_experience,
                   hp, attack, defense, special_attack, special_defense, speed,
                   generation, description, genus, color, shape, habitat,
                   is_legendary, is_mythical, sprite_url, artwork_url
            FROM pokemon
            WHERE id = %s
            """,
            (pokemon_id,),
        ).fetchone()

        if pokemon is None:
            raise HTTPException(status_code=404, detail="Pokemon not found")

        moves = conn.execute(
            """
            SELECT m.id, m.name
            FROM moves m
            JOIN pokemon_moves pm ON pm.move_id = m.id
            WHERE pm.pokemon_id = %s
            ORDER BY m.name
            """,
            (pokemon_id,),
        ).fetchall()

        abilities = conn.execute(
            """
            SELECT a.id, a.name
            FROM abilities a
            JOIN pokemon_abilities pa ON pa.ability_id = a.id
            WHERE pa.pokemon_id = %s
            ORDER BY a.name
            """,
            (pokemon_id,),
        ).fetchall()

    return {
        "id": pokemon["id"],
        "name": pokemon["name"],
        "height_decimetres": pokemon["height_dm"],
        "weight_hectograms": pokemon["weight_hg"],
        "base_experience": pokemon["base_experience"],
        "types": pokemon["types"],
        "stats": {
            "hp": pokemon["hp"],
            "attack": pokemon["attack"],
            "defense": pokemon["defense"],
            "special-attack": pokemon["special_attack"],
            "special-defense": pokemon["special_defense"],
            "speed": pokemon["speed"],
        },
        "abilities": abilities,
        "moves": moves,
        "species": {
            "generation": pokemon["generation"],
            "description": pokemon["description"],
            "genus": pokemon["genus"],
            "color": pokemon["color"],
            "shape": pokemon["shape"],
            "habitat": pokemon["habitat"],
            "is_legendary": pokemon["is_legendary"],
            "is_mythical": pokemon["is_mythical"],
        },
        "images": {
            "sprite": pokemon["sprite_url"],
            "official_artwork": pokemon["artwork_url"],
        },
    }


@app.get("/move/{move_id}")
def get_move(move_id: int):
    with get_connection() as conn:
        move = conn.execute(
            """
            SELECT id, name, type, power, pp, accuracy, priority, damage_class,
                   effect_chance, effect, short_effect, generation
            FROM moves
            WHERE id = %s
            """,
            (move_id,),
        ).fetchone()

        if move is None:
            raise HTTPException(status_code=404, detail="Move not found")

        pokemon = conn.execute(
            """
            SELECT p.id, p.name
            FROM pokemon p
            JOIN pokemon_moves pm ON pm.pokemon_id = p.id
            WHERE pm.move_id = %s
            ORDER BY p.name
            """,
            (move_id,),
        ).fetchall()

    move["learned_by_pokemon"] = pokemon
    return move


@app.get("/ability/{ability_id}")
def get_ability(ability_id: int):
    with get_connection() as conn:
        ability = conn.execute(
            """
            SELECT id, name, effect, short_effect, generation, is_main_series
            FROM abilities
            WHERE id = %s
            """,
            (ability_id,),
        ).fetchone()

        if ability is None:
            raise HTTPException(status_code=404, detail="Ability not found")

        pokemon = conn.execute(
            """
            SELECT p.id, p.name
            FROM pokemon p
            JOIN pokemon_abilities pa ON pa.pokemon_id = p.id
            WHERE pa.ability_id = %s
            ORDER BY p.name
            """,
            (ability_id,),
        ).fetchall()

    ability["pokemon"] = pokemon
    return ability
