from psycopg import sql

# Minimum trigram similarity for a name to match the query (0 = anything, 1 = exact).
NAME_SIMILARITY_THRESHOLD = 0.3

# Keep a row if it has at least one of the selected types.
TYPE_CONDITIONS = {
    "pokemon": "types && %(types)s",  # Pokemon have a list of types: the lists must overlap.
    "moves": "type = ANY(%(types)s)",  # Moves have a single type.
}


# Pokemon

def pokemon_by_id(conn, pokemon_id):
    return conn.execute(
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


def moves_by_pokemon_id(conn, pokemon_id):
    return conn.execute(
        """
        SELECT m.id, m.name
        FROM moves m
        JOIN pokemon_moves pm ON pm.move_id = m.id
        WHERE pm.pokemon_id = %s
        ORDER BY m.name
        """,
        (pokemon_id,),
    ).fetchall()


def abilities_by_pokemon_id(conn, pokemon_id):
    return conn.execute(
        """
        SELECT a.id, a.name
        FROM abilities a
        JOIN pokemon_abilities pa ON pa.ability_id = a.id
        WHERE pa.pokemon_id = %s
        ORDER BY a.name
        """,
        (pokemon_id,),
    ).fetchall()


# Moves

def move_by_id(conn, move_id):
    return conn.execute(
        """
        SELECT id, name, type, power, pp, accuracy, priority, damage_class,
               effect_chance, effect, short_effect, generation
        FROM moves
        WHERE id = %s
        """,
        (move_id,),
    ).fetchone()


def pokemon_by_move_id(conn, move_id):
    return conn.execute(
        """
        SELECT p.id, p.name
        FROM pokemon p
        JOIN pokemon_moves pm ON pm.pokemon_id = p.id
        WHERE pm.move_id = %s
        ORDER BY p.name
        """,
        (move_id,),
    ).fetchall()


# Abilities

def ability_by_id(conn, ability_id):
    return conn.execute(
        """
        SELECT id, name, effect, short_effect, generation, is_main_series
        FROM abilities
        WHERE id = %s
        """,
        (ability_id,),
    ).fetchone()


def pokemon_by_ability_id(conn, ability_id):
    return conn.execute(
        """
        SELECT p.id, p.name
        FROM pokemon p
        JOIN pokemon_abilities pa ON pa.pokemon_id = p.id
        WHERE pa.ability_id = %s
        ORDER BY p.name
        """,
        (ability_id,),
    ).fetchall()


# Stat bounds

def pokemon_stat_bounds(conn):
    return conn.execute(
        """
        SELECT MIN(hp) AS min_hp, MAX(hp) AS max_hp,
               MIN(attack) AS min_attack, MAX(attack) AS max_attack,
               MIN(defense) AS min_defense, MAX(defense) AS max_defense,
               MIN(special_attack) AS min_special_attack, MAX(special_attack) AS max_special_attack,
               MIN(special_defense) AS min_special_defense, MAX(special_defense) AS max_special_defense,
               MIN(speed) AS min_speed, MAX(speed) AS max_speed
        FROM pokemon
        """
    ).fetchone()


def move_stat_bounds(conn):
    return conn.execute(
        """
        SELECT MIN(power) AS min_power, MAX(power) AS max_power,
               MIN(accuracy) AS min_accuracy, MAX(accuracy) AS max_accuracy,
               MIN(pp) AS min_pp, MAX(pp) AS max_pp,
               MIN(priority) AS min_priority, MAX(priority) AS max_priority,
               MIN(effect_chance) AS min_effect_chance, MAX(effect_chance) AS max_effect_chance
        FROM moves
        """
    ).fetchone()


# Types

def all_types(conn):
    # Every type used by at least one Pokemon or one move, e.g. ["bug", "dark", ...].
    rows = conn.execute(
        """
        SELECT unnest(types) AS type FROM pokemon
        UNION
        SELECT type FROM moves
        ORDER BY type
        """
    ).fetchall()
    return [row["type"] for row in rows]


# Search

def build_filters(table, minimums, maximums, types):
    # minimums / maximums: {column: value}, e.g. {"speed": 90}. types: e.g. ["fire", "water"].
    # Returns the SQL conditions and the values for their placeholders.
    conditions = []
    values = {}

    if types and table in TYPE_CONDITIONS:
        values["types"] = types
        conditions.append(sql.SQL(TYPE_CONDITIONS[table]))

    for bounds, operator, suffix in [(minimums, ">=", "min"), (maximums, "<=", "max")]:
        for column, value in bounds.items():
            key = f"{column}_{suffix}"
            values[key] = value
            conditions.append(
                sql.SQL("{} {} {}").format(
                    sql.Identifier(column), sql.SQL(operator), sql.Placeholder(key)
                )
            )

    return conditions, values


def search(conn, table, columns, query_text, minimums, maximums, types):
    conditions, values = build_filters(table, minimums, maximums, types)

    # Fuzzy name search: names are compared without hyphens ("thunder-punch" -> "thunder punch").
    # word_similarity handles typos and partial names, starts_with ranks prefixes first.
    query_text = query_text.strip().lower().replace("-", " ")
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

    query = sql.SQL("SELECT {columns} FROM {table}").format(
        columns=sql.SQL(", ").join(sql.Identifier(c) for c in columns),
        table=sql.Identifier(table),
    )
    if conditions:
        query += sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions)
    query += sql.SQL(" ORDER BY ") + order_by

    return conn.execute(query, values).fetchall()
