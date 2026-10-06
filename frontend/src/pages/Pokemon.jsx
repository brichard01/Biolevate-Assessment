import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import "./Pokemon.css";

const STATS = [
    { name: "hp", label: "HP" },
    { name: "attack", label: "Attack" },
    { name: "defense", label: "Defense" },
    { name: "special_attack", label: "Special Attack" },
    { name: "special_defense", label: "Special Defense" },
    { name: "speed", label: "Speed" },
];

function Pokemon() {
    const [searchParams] = useSearchParams();
    const id = searchParams.get("id");

    const [pokemon, setPokemon] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (id) {
            fetch(`http://localhost:8000/pokemon/${id}`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Pokémon not found.");
                    }

                    return response.json();
                })
                .then((data) => {
                    setPokemon(data);
                })
                .catch((error) => {
                    setError(error.message);
                });
        }
    }, [id]);

    const errorMessage = id ? error : "No Pokémon ID provided.";

    if (errorMessage) {
        return (
            <main className="pokemon-page">
                <div className="pokemon-error">
                    <h1>Oops!</h1>
                    <p>{errorMessage}</p>
                </div>
            </main>
        );
    }

    if (!pokemon) {
        return (
            <main className="pokemon-page">
                <div className="pokemon-loading">
                    Loading Pokémon...
                </div>
            </main>
        );
    }

    return (
        <main className="pokemon-page">
            <div className="pokemon-container">

                {/* Header */}
                <section className="pokemon-hero">
                    <div className="pokemon-number">
                        #{String(pokemon.id).padStart(3, "0")}
                    </div>

                    <div className="pokemon-image-container">
                        <img
                            src={pokemon.artwork_url}
                            alt={pokemon.name}
                            className="pokemon-image"
                        />
                    </div>

                    <div className="pokemon-header">
                        <h1>{pokemon.name}</h1>

                        <div className="pokemon-types">
                            {pokemon.types.map((type) => (
                                <span key={type} className={`type type-${type}`}>
                                    {type}
                                </span>
                            ))}
                        </div>
                    </div>
                </section>

                {/* Description */}
                <section className="pokemon-section pokemon-description">
                    <p>{pokemon.description}</p>

                    <span className="pokemon-genus">
                        {pokemon.genus}
                    </span>
                </section>

                {/* Physical information */}
                <section className="pokemon-section">
                    <h2>Profile</h2>

                    <div className="profile-grid">
                        <div className="profile-item">
                            <span>Height</span>
                            <strong>{pokemon.height_dm / 10} m</strong>
                        </div>

                        <div className="profile-item">
                            <span>Weight</span>
                            <strong>{pokemon.weight_hg / 10} kg</strong>
                        </div>

                        <div className="profile-item">
                            <span>Color</span>
                            <strong>{pokemon.color}</strong>
                        </div>

                        <div className="profile-item">
                            <span>Habitat</span>
                            <strong>{pokemon.habitat}</strong>
                        </div>

                        <div className="profile-item">
                            <span>Generation</span>
                            <strong>{pokemon.generation}</strong>
                        </div>

                        <div className="profile-item">
                            <span>Base XP</span>
                            <strong>{pokemon.base_experience}</strong>
                        </div>
                    </div>
                </section>

                {/* Base stats */}
                <section className="pokemon-section">
                    <h2>Base Stats</h2>

                    <div className="stats">
                        {STATS.map((stat) => (
                            <div className="stat" key={stat.name}>
                                <div className="stat-header">
                                    <span>{stat.label}</span>
                                    <strong>{pokemon[stat.name]}</strong>
                                </div>

                                <div className="stat-bar">
                                    <div
                                        className="stat-bar-fill"
                                        style={{ width: `${(pokemon[stat.name] / pokemon.max_stats[stat.name]) * 100}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Abilities */}
                <section className="pokemon-section">
                    <h2>Abilities</h2>

                    <div className="tags">
                        {pokemon.abilities.map((ability) => (
                            <Link to={`/ability?id=${ability.id}`} className="tag" key={ability.id}>
                                {ability.name}
                            </Link>
                        ))}
                    </div>
                </section>

                {/* Moves */}
                <section className="pokemon-section">
                    <h2>Moves</h2>

                    <div className="tags moves">
                        {pokemon.moves.map((move) => (
                            <Link to={`/move?id=${move.id}`} className="tag" key={move.id}>
                                {move.name}
                            </Link>
                        ))}
                    </div>
                </section>

            </div>
        </main>
    );
}

export default Pokemon;