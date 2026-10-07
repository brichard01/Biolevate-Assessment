from fastapi.testclient import TestClient
import embeddings
from main import app

client = TestClient(app)


def search(**params):
    response = client.get("/search", params=params)
    assert response.status_code == 200
    return response.json()["results"]


def names(results):
    return [result["name"] for result in results]


# Successful retrieval

def test_get_pokemon():
    response = client.get("/pokemon/25")
    assert response.status_code == 200
    pokemon = response.json()
    assert pokemon["name"] == "pikachu"
    assert pokemon["types"] == ["electric"]
    assert {"id": 85, "name": "thunderbolt"} in pokemon["moves"]
    assert pokemon["stat_bounds"]["max_hp"] == 250


def test_get_move_and_ability_with_their_pokemon():
    move = client.get("/move/1").json()
    ability = client.get("/ability/1").json()
    assert move["name"] == "pound"
    assert {"id": 113, "name": "chansey"} in move["learned_by_pokemon"]
    assert ability["name"] == "stench"
    assert {"id": 88, "name": "grimer"} in ability["pokemon"]



# Invalid input

def test_unknown_id_returns_404():
    assert client.get("/pokemon/9999").status_code == 404
    assert client.get("/move/9999").status_code == 404
    assert client.get("/ability/2").status_code == 404


def test_invalid_search_parameters_return_400():
    invalid_params = [
        {"category": "item"},
        {"category": "pokemon", "mode": "magic"},
        {"category": "pokemon", "speed_min": "fast"},
        {"category": "pokemon", "q": "a" * 101},
    ]

    for params in invalid_params:
        assert client.get("/search", params=params).status_code == 400, params


def test_missing_category_is_rejected():
    assert client.get("/search").status_code == 422


# Name search: partial names and typos

def test_name_search_finds_partial_name_first():
    assert names(search(category="pokemon", q="bulba"))[0] == "bulbasaur"


def test_name_search_ranks_prefix_matches_first():
    top_three = names(search(category="pokemon", q="char"))[:3]
    assert set(top_three) == {"charmander", "charmeleon", "charizard"}


def test_name_search_tolerates_typos():
    assert "pikachu" in names(search(category="pokemon", q="pikchu"))[:3]
    assert names(search(category="move", q="thder pnch"))[0] == "thunder-punch"


# Filters

def test_fast_electric_pokemon():
    results = search(category="pokemon", types="electric", speed_min=100)
    assert results
    for pokemon in results:
        assert "electric" in pokemon["types"]
        assert pokemon["speed"] >= 100


def test_type_filter_keeps_any_selected_type():
    results = search(category="pokemon", types=["fire", "water"])
    assert results
    for pokemon in results:
        assert "fire" in pokemon["types"] or "water" in pokemon["types"]


# Description search: keywords and meaning

def test_description_search_finds_sleep_moves():
    top_five = names(search(category="move", q="put the opponent to sleep", mode="description"))[:5]
    assert set(top_five) == {"sing", "sleep-powder", "hypnosis", "lovely-kiss", "spore"}


def test_description_search_understands_synonyms():
    # "fall asleep" shares no keyword with "Puts the target to sleep": only the vectors find it.
    results = search(category="move", q="make the enemy fall asleep", mode="description", types="grass")
    assert set(names(results)[:2]) == {"sleep-powder", "spore"}


def test_description_search_finds_rain_abilities():
    top_five = names(search(category="ability", q="rain", mode="description"))[:5]
    assert "swift-swim" in top_five
    assert "rain-dish" in top_five

