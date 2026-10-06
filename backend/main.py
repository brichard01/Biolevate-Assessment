import os

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
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
            SELECT m.name
            FROM moves m
            JOIN pokemon_moves pm ON pm.move_id = m.id
            WHERE pm.pokemon_id = %s
            ORDER BY m.name
            """,
            (pokemon_id,),
        ).fetchall()

        abilities = conn.execute(
            """
            SELECT a.name
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
        "abilities": [ability["name"] for ability in abilities],
        "moves": [move["name"] for move in moves],
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


@app.get("/moves/{move_id}")
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
            SELECT p.name
            FROM pokemon p
            JOIN pokemon_moves pm ON pm.pokemon_id = p.id
            WHERE pm.move_id = %s
            ORDER BY p.name
            """,
            (move_id,),
        ).fetchall()

    move["learned_by_pokemon"] = [p["name"] for p in pokemon]
    return move


@app.get("/abilities/{ability_id}")
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
            SELECT p.name
            FROM pokemon p
            JOIN pokemon_abilities pa ON pa.pokemon_id = p.id
            WHERE pa.ability_id = %s
            ORDER BY p.name
            """,
            (ability_id,),
        ).fetchall()

    ability["pokemon"] = [p["name"] for p in pokemon]
    return ability
