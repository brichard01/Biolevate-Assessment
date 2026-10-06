import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import "./Move.css";

function Move() {
    const [searchParams] = useSearchParams();
    const id = searchParams.get("id");

    const [move, setMove] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!id) {
            setError("No move ID provided.");
            return;
        }

        fetch(`http://localhost:8000/move/${id}`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Move not found.");
                }

                return response.json();
            })
            .then((data) => {
                setMove(data);
            })
            .catch((error) => {
                setError(error.message);
            });
    }, [id]);

    if (error) {
        return (
            <main className="move-page">
                <div className="move-error">
                    <h1>Oops!</h1>
                    <p>{error}</p>
                </div>
            </main>
        );
    }

    if (!move) {
        return (
            <main className="move-page">
                <div className="move-loading">
                    Loading move...
                </div>
            </main>
        );
    }

    return (
        <main className="move-page">
            <div className="move-container">

                {/* Header */}
                <section className="move-hero">
                    <div className="move-number">
                        #{String(move.id).padStart(3, "0")}
                    </div>

                    <h1>{move.name.replaceAll("-", " ")}</h1>

                    <div className="move-types">
                        <span className="type">{move.type}</span>
                        <span className="type">{move.damage_class}</span>
                    </div>
                </section>

                {/* Effect */}
                <section className="move-section move-description">
                    <p>{move.effect}</p>

                    <span className="move-short-effect">
                        {move.short_effect}
                    </span>
                </section>

                {/* Details */}
                <section className="move-section">
                    <h2>Details</h2>

                    <div className="profile-grid">
                        <div className="profile-item">
                            <span>Power</span>
                            <strong>{move.power ?? "—"}</strong>
                        </div>

                        <div className="profile-item">
                            <span>Accuracy</span>
                            <strong>{move.accuracy ? `${move.accuracy}%` : "—"}</strong>
                        </div>

                        <div className="profile-item">
                            <span>PP</span>
                            <strong>{move.pp}</strong>
                        </div>

                        <div className="profile-item">
                            <span>Priority</span>
                            <strong>{move.priority}</strong>
                        </div>

                        <div className="profile-item">
                            <span>Effect Chance</span>
                            <strong>{move.effect_chance ? `${move.effect_chance}%` : "—"}</strong>
                        </div>

                        <div className="profile-item">
                            <span>Generation</span>
                            <strong>{move.generation}</strong>
                        </div>
                    </div>
                </section>

                {/* Learned by */}
                <section className="move-section">
                    <h2>Learned By</h2>

                    <div className="tags">
                        {move.learned_by_pokemon.map((pokemon) => (
                            <Link to={`/pokemon?id=${pokemon.id}`} className="tag" key={pokemon.id}>
                                {pokemon.name}
                            </Link>
                        ))}
                    </div>
                </section>

            </div>
        </main>
    );
}

export default Move;
