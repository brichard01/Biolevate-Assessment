import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import "./Pokemon.css";

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
                            src={pokemon.images.official_artwork}
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
                    <p>{pokemon.species.description}</p>

                    <span className="pokemon-genus">
                        {pokemon.species.genus}
                    </span>
                </section>

                {/* Physical information */}
                <section className="pokemon-section">
                    <h2>Profile</h2>

                    <div className="profile-grid">
                        <div className="profile-item">
                            <span>Height</span>
                            <strong>{pokemon.height_decimetres / 10} m</strong>
                        </div>

                        <div className="profile-item">
                            <span>Weight</span>
                            <strong>{pokemon.weight_hectograms / 10} kg</strong>
                        </div>

                        <div className="profile-item">
                            <span>Color</span>
                            <strong>{pokemon.species.color}</strong>
                        </div>

                        <div className="profile-item">
                            <span>Habitat</span>
                            <strong>{pokemon.species.habitat}</strong>
                        </div>

                        <div className="profile-item">
                            <span>Generation</span>
                            <strong>{pokemon.species.generation}</strong>
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
                        {Object.entries(pokemon.stats).map(([stat, value]) => (
                            <div className="stat" key={stat}>
                                <div className="stat-header">
                                    <span>{stat.replace("-", " ")}</span>
                                    <strong>{value}</strong>
                                </div>

                                <div className="stat-bar">
                                    <div
                                        className="stat-bar-fill"
                                        style={{ width: `${Math.min(value, 100)}%` }}
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