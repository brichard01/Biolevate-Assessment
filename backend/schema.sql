CREATE EXTENSION IF NOT EXISTS pg_search;
CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS pokemon_moves, pokemon_abilities, pokemon, moves, abilities;

CREATE TABLE pokemon (
    id               INT PRIMARY KEY,
    name             TEXT NOT NULL UNIQUE,
    types            TEXT[] NOT NULL,
    height_dm        INT NOT NULL,
    weight_hg        INT NOT NULL,
    base_experience  INT NOT NULL,
    hp               INT NOT NULL,
    attack           INT NOT NULL,
    defense          INT NOT NULL,
    special_attack   INT NOT NULL,
    special_defense  INT NOT NULL,
    speed            INT NOT NULL,
    generation       TEXT NOT NULL,
    description      TEXT NOT NULL,
    genus            TEXT NOT NULL,
    color            TEXT NOT NULL,
    shape            TEXT NOT NULL,
    habitat          TEXT NOT NULL,
    is_legendary     BOOLEAN NOT NULL,
    is_mythical      BOOLEAN NOT NULL,
    sprite_url       TEXT,
    artwork_url      TEXT,
    embedding        VECTOR(384)
);

CREATE TABLE moves (
    id            INT PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    type          TEXT NOT NULL,
    damage_class  TEXT NOT NULL,
    power         INT,
    accuracy      INT,
    pp            INT NOT NULL,
    priority      INT NOT NULL,
    effect_chance INT,
    effect        TEXT NOT NULL,
    short_effect  TEXT NOT NULL,
    generation    TEXT NOT NULL,
    embedding     VECTOR(384)
);

CREATE TABLE abilities (
    id             INT PRIMARY KEY,
    name           TEXT NOT NULL UNIQUE,
    effect         TEXT NOT NULL,
    short_effect   TEXT NOT NULL,
    generation     TEXT NOT NULL,
    is_main_series BOOLEAN NOT NULL,
    embedding      VECTOR(384)
);

CREATE TABLE pokemon_moves (
    pokemon_id INT REFERENCES pokemon(id),
    move_id    INT REFERENCES moves(id),
    PRIMARY KEY (pokemon_id, move_id)
);

CREATE TABLE pokemon_abilities (
    pokemon_id INT REFERENCES pokemon(id),
    ability_id INT REFERENCES abilities(id),
    PRIMARY KEY (pokemon_id, ability_id)
);

CREATE INDEX ON pokemon USING GIN (types);
CREATE INDEX ON pokemon (speed);
CREATE INDEX ON pokemon_moves (move_id);
CREATE INDEX ON pokemon_abilities (ability_id);

CREATE INDEX ON pokemon   USING bm25 (id, name, genus, description) WITH (key_field = 'id');
CREATE INDEX ON moves     USING bm25 (id, name, effect, type)       WITH (key_field = 'id');
CREATE INDEX ON abilities USING bm25 (id, name, effect)             WITH (key_field = 'id');

CREATE INDEX ON pokemon   USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON moves     USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON abilities USING hnsw (embedding vector_cosine_ops);
