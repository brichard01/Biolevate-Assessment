import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

DATA_FILE = "data/pokedex.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    pokedex_data = json.load(f)

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

@app.get("/pokemon/{pokemon_id}")
def get_pokemon(pokemon_id: int):
    for pokemon in pokedex_data["pokemon"]:
        if pokemon["id"] == pokemon_id:
            return pokemon

    raise HTTPException(status_code=404, detail="Pokemon not found")

@app.get("/moves/{move_id}")
def get_move(move_id: int):
    for move in pokedex_data["moves"]:
        if move["id"] == move_id:
            return move

    raise HTTPException(status_code=404, detail="Move not found")

@app.get("/abilities/{ability_id}")
def get_ability(ability_id: int):
    for ability in pokedex_data["abilities"]:
        if ability["id"] == ability_id:
            return ability

    raise HTTPException(status_code=404, detail="Ability not found")
