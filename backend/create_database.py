import hashlib
import json

import psycopg

from config import DATABASE_URL
from embeddings import embed, to_pgvector

DATA_FILE = "data/pokedex.json"
DATA_SHA256 = "251b7a02837bcb01a491e40de488ef179c95df7d7cb7e0aec1f4562d9d16cadb"
SCHEMA_FILE = "schema.sql"


def load_pokedex():
    with open(DATA_FILE, "rb") as f:
        content = f.read()

    if hashlib.sha256(content).hexdigest() != DATA_SHA256:
        raise ValueError(f"{DATA_FILE} does not match the published checksum")

    return json.loads(content)


def insert_pokemon(cur, pokemon_list):
    cur.executemany(
        """
        INSERT INTO pokemon (
            id, name, types, height_dm, weight_hg, base_experience,
            hp, attack, defense, special_attack, special_defense, speed,
            generation, description, genus, color, shape, habitat,
            is_legendary, is_mythical, sprite_url, artwork_url
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        """,
        [
            (
                p["id"], p["name"], p["types"], p["height_decimetres"],
                p["weight_hectograms"], p["base_experience"],
                p["stats"]["hp"], p["stats"]["attack"], p["stats"]["defense"],
                p["stats"]["special-attack"], p["stats"]["special-defense"],
                p["stats"]["speed"],
                p["species"]["generation"], p["species"]["description"],
                p["species"]["genus"], p["species"]["color"],
                p["species"]["shape"], p["species"]["habitat"],
                p["species"]["is_legendary"], p["species"]["is_mythical"],
                p["images"]["sprite"], p["images"]["official_artwork"],
            )
            for p in pokemon_list
        ],
    )


def insert_moves(cur, moves):
    cur.executemany(
        """
        INSERT INTO moves (
            id, name, type, damage_class, power, accuracy, pp, priority,
            effect_chance, effect, short_effect, generation
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                m["id"], m["name"], m["type"], m["damage_class"], m["power"],
                m["accuracy"], m["pp"], m["priority"], m["effect_chance"],
                m["effect"], m["short_effect"], m["generation"],
            )
            for m in moves
        ],
    )


def insert_abilities(cur, abilities):
    cur.executemany(
        """
        INSERT INTO abilities (
            id, name, effect, short_effect, generation, is_main_series
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """,
        [
            (
                a["id"], a["name"], a["effect"], a["short_effect"],
                a["generation"], a["is_main_series"],
            )
            for a in abilities
        ],
    )


def insert_relations(cur, pokedex):
    move_ids = {m["name"]: m["id"] for m in pokedex["moves"]}
    ability_ids = {a["name"]: a["id"] for a in pokedex["abilities"]}

    cur.executemany(
        "INSERT INTO pokemon_moves (pokemon_id, move_id) VALUES (%s, %s)",
        [
            (p["id"], move_ids[move])
            for p in pokedex["pokemon"]
            for move in p["moves"]
        ],
    )

    cur.executemany(
        "INSERT INTO pokemon_abilities (pokemon_id, ability_id) VALUES (%s, %s)",
        [
            (p["id"], ability_ids[ability])
            for p in pokedex["pokemon"]
            for ability in p["abilities"]
        ],
    )


def insert_embeddings(cur, table, text_column):
    # Vector of each row's text (description or effect), used by the vector search.
    cur.execute(f"SELECT id, {text_column} FROM {table} ORDER BY id")
    rows = cur.fetchall()
    vectors = embed([text for _, text in rows])

    cur.executemany(
        f"UPDATE {table} SET embedding = %s::vector WHERE id = %s",
        [(to_pgvector(vector), row_id) for (row_id, _), vector in zip(rows, vectors)],
    )


def main():
    pokedex = load_pokedex()

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = f.read()

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(schema)
            insert_pokemon(cur, pokedex["pokemon"])
            insert_moves(cur, pokedex["moves"])
            insert_abilities(cur, pokedex["abilities"])
            insert_relations(cur, pokedex)

            insert_embeddings(cur, "pokemon", "description")
            insert_embeddings(cur, "moves", "effect")
            insert_embeddings(cur, "abilities", "effect")

            for table in ["pokemon", "moves", "abilities", "pokemon_moves", "pokemon_abilities"]:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                print(f"{table}: {cur.fetchone()[0]}")

            for table in ["pokemon", "moves", "abilities"]:
                cur.execute(f"SELECT COUNT(*) FROM {table} WHERE embedding IS NOT NULL")
                print(f"{table} with embedding: {cur.fetchone()[0]}")


if __name__ == "__main__":
    main()
