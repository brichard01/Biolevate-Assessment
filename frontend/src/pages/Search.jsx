import { useState } from "react";
import { Link } from "react-router-dom";
import "./Search.css";

// Each filter is a numeric range: sent as <name>_min and <name>_max.
const CATEGORIES = {
    pokemon: {
        label: "Pokémon",
        filters: [
            { name: "hp", label: "HP" },
            { name: "attack", label: "Attack" },
            { name: "defense", label: "Defense" },
            { name: "special_attack", label: "Sp. Attack" },
            { name: "special_defense", label: "Sp. Defense" },
            { name: "speed", label: "Speed" },
        ],
    },
    move: {
        label: "Moves",
        filters: [
            { name: "power", label: "Power" },
            { name: "accuracy", label: "Accuracy" },
            { name: "pp", label: "PP" },
            { name: "priority", label: "Priority" },
            { name: "effect_chance", label: "Effect Chance" },
        ],
    },
    ability: {
        label: "Abilities",
        filters: [],
    },
};

function formatName(name) {
    return name.replaceAll("-", " ");
}

function PokemonPreview({ pokemon }) {
    return (
        <div className="preview">
            <img src={pokemon.sprite_url} alt={pokemon.name} className="preview-sprite" />

            <div className="preview-body">
                <div className="preview-header">
                    <strong>{formatName(pokemon.name)}</strong>
                    <span className="preview-number">#{String(pokemon.id).padStart(3, "0")}</span>
                    {pokemon.types.map((type) => (
                        <span className="preview-tag" key={type}>{type}</span>
                    ))}
                </div>

                <div className="preview-stats">
                    {CATEGORIES.pokemon.filters.map((stat) => (
                        <span key={stat.name}>
                            {stat.label} <b>{pokemon[stat.name]}</b>
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
}

function MovePreview({ move }) {
    return (
        <div className="preview-body">
            <div className="preview-header">
                <strong>{formatName(move.name)}</strong>
                <span className="preview-tag">{move.type}</span>
                <span className="preview-tag">{move.damage_class}</span>
            </div>

            <div className="preview-stats">
                {CATEGORIES.move.filters.map((field) => (
                    <span key={field.name}>
                        {field.label} <b>{move[field.name] ?? "—"}</b>
                    </span>
                ))}
            </div>

            <p className="preview-effect">{move.short_effect}</p>
        </div>
    );
}

function AbilityPreview({ ability }) {
    return (
        <div className="preview-body">
            <div className="preview-header">
                <strong>{formatName(ability.name)}</strong>
            </div>

            <p className="preview-effect">{ability.short_effect}</p>
        </div>
    );
}

function Search() {
    const [category, setCategory] = useState("pokemon");
    const [query, setQuery] = useState("");
    const [filterValues, setFilterValues] = useState({});

    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const { filters } = CATEGORIES[category];
    const activeFilters = Object.entries(filterValues).filter(([, value]) => value !== "");

    function changeCategory(newCategory) {
        setCategory(newCategory);
        setFilterValues({});
        setResults(null);
        setError(null);
    }

    function changeFilter(key, value) {
        setFilterValues({ ...filterValues, [key]: value });
    }

    function handleSubmit(event) {
        event.preventDefault();

        const params = new URLSearchParams({ category, q: query.trim() });
        for (const [key, value] of activeFilters) {
            params.set(key, value);
        }

        setLoading(true);
        setError(null);

        fetch(`http://localhost:8000/search?${params}`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Search failed. Please try again.");
                }

                return response.json();
            })
            .then((data) => {
                setResults(data.results);
            })
            .catch((error) => {
                setError(error.message);
            })
            .finally(() => {
                setLoading(false);
            });
    }

    return (
        <main className="search-page">
            <div className="search-container">

                <h1>Pokédex Search</h1>

                {/* Category */}
                <div className="search-categories">
                    {Object.entries(CATEGORIES).map(([key, { label }]) => (
                        <button
                            key={key}
                            type="button"
                            className={key === category ? "category active" : "category"}
                            onClick={() => changeCategory(key)}
                        >
                            {label}
                        </button>
                    ))}
                </div>

                <form onSubmit={handleSubmit}>

                    {/* Query */}
                    <div className="search-form">
                        <input
                            type="text"
                            value={query}
                            onChange={(event) => setQuery(event.target.value)}
                            placeholder={`Search ${CATEGORIES[category].label.toLowerCase()}...`}
                        />

                        <button type="submit" disabled={loading}>
                            Search
                        </button>
                    </div>

                    {/* Filters */}
                    {filters.length > 0 && (
                        <div className="search-filters">
                            {filters.map((filter) => (
                                <div className="search-filter" key={filter.name}>
                                    <span>{filter.label}</span>

                                    <div className="search-filter-range">
                                        <input
                                            type="number"
                                            placeholder="Min"
                                            aria-label={`${filter.label} min`}
                                            value={filterValues[`${filter.name}_min`] ?? ""}
                                            onChange={(event) => changeFilter(`${filter.name}_min`, event.target.value)}
                                        />
                                        <input
                                            type="number"
                                            placeholder="Max"
                                            aria-label={`${filter.label} max`}
                                            value={filterValues[`${filter.name}_max`] ?? ""}
                                            onChange={(event) => changeFilter(`${filter.name}_max`, event.target.value)}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                </form>

                {/* Results */}
                {loading && <p className="search-message">Searching...</p>}

                {error && <p className="search-message search-error">{error}</p>}

                {!loading && !error && results && results.length === 0 && (
                    <p className="search-message">No results found.</p>
                )}

                {!loading && !error && results && results.length > 0 && (
                    <ul className="search-results">
                        {results.map((result) => (
                            <li key={result.id}>
                                <Link to={`/${category}?id=${result.id}`} className="search-result">
                                    {category === "pokemon" && <PokemonPreview pokemon={result} />}
                                    {category === "move" && <MovePreview move={result} />}
                                    {category === "ability" && <AbilityPreview ability={result} />}
                                </Link>
                            </li>
                        ))}
                    </ul>
                )}

            </div>
        </main>
    );
}

export default Search;
