import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import "./Ability.css";

function Ability() {
    const [searchParams] = useSearchParams();
    const id = searchParams.get("id");

    const [ability, setAbility] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (id) {
            fetch(`http://localhost:8000/ability/${id}`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Ability not found.");
                    }

                    return response.json();
                })
                .then((data) => {
                    setAbility(data);
                })
                .catch((error) => {
                    setError(error.message);
                });
        }
    }, [id]);

    const errorMessage = id ? error : "No ability ID provided.";

    if (errorMessage) {
        return (
            <main className="ability-page">
                <div className="ability-error">
                    <h1>Oops!</h1>
                    <p>{errorMessage}</p>
                </div>
            </main>
        );
    }

    if (!ability) {
        return (
            <main className="ability-page">
                <div className="ability-loading">
                    Loading ability...
                </div>
            </main>
        );
    }

    return (
        <main className="ability-page">
            <div className="ability-container">

                {/* Header */}
                <section className="ability-hero">
                    <div className="ability-number">
                        #{String(ability.id).padStart(3, "0")}
                    </div>

                    <h1>{ability.name.replaceAll("-", " ")}</h1>

                    <div className="ability-types">
                        <span className="type">{ability.generation}</span>
                    </div>
                </section>

                {/* Effect */}
                <section className="ability-section ability-description">
                    <p>{ability.effect}</p>

                    <span className="ability-short-effect">
                        {ability.short_effect}
                    </span>
                </section>

                {/* Pokemon */}
                <section className="ability-section">
                    <h2>Pokémon</h2>

                    <div className="tags">
                        {ability.pokemon.map((pokemon) => (
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

export default Ability;
