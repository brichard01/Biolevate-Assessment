import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./Search.css";

// Each filter is a numeric range: sent as <name>_min and <name>_max.
// typeFilter: whether results can be filtered by type.
const CATEGORIES = {
    pokemon: {
        label: "Pokémon",
        typeFilter: true,
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
        typeFilter: true,
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
        typeFilter: false,
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

function fetchResults(category, query, filterValues, types) {
    const params = new URLSearchParams({ category, q: query.trim() });
    for (const [key, value] of Object.entries(filterValues)) {
        if (value !== "") {
            params.set(key, value);
        }
    }
    for (const type of types) {
        params.append("types", type);
    }

    return fetch(`http://localhost:8000/search?${params}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error("Search failed. Please try again.");
            }

            return response.json();
        })
        .then((data) => data.results);
}

// Slider with two handles. The colored part between the handles is the selected range.
function RangeFilter({ label, bounds, min, max, onChange }) {
    const left = ((min - bounds.min) / (bounds.max - bounds.min)) * 100;
    const right = ((max - bounds.min) / (bounds.max - bounds.min)) * 100;

    // When both handles are at the far right, only the min handle can move.
    const minOnTop = min === bounds.max;

    return (
        <div className="search-filter">
            <div className="search-filter-header">
                <span>{label}</span>
                <strong>{min} – {max}</strong>
            </div>

            <div className="range-slider">
                <div className="range-track" />
                <div className="range-fill" style={{ left: `${left}%`, width: `${right - left}%` }} />

                <input
                    type="range"
                    min={bounds.min}
                    max={bounds.max}
                    value={min}
                    aria-label={`${label} min`}
                    onChange={(event) => onChange(Math.min(Number(event.target.value), max), max)}
                    style={minOnTop ? { zIndex: 1 } : undefined}
                />
                <input
                    type="range"
                    min={bounds.min}
                    max={bounds.max}
                    value={max}
                    aria-label={`${label} max`}
                    onChange={(event) => onChange(min, Math.max(Number(event.target.value), min))}
                />
            </div>
        </div>
    );
}

// Dropdown with one checkbox per type. Results keep items having at least one checked type.
function TypeFilter({ types, selected, onToggle, open, onOpenChange }) {
    return (
        <details
            className="type-filter"
            open={open}
            onToggle={(event) => onOpenChange(event.currentTarget.open)}
        >
            <summary>
                <span>Types</span>
                <strong>{selected.length > 0 ? selected.join(", ") : "Any"}</strong>
            </summary>

            <div className="type-options">
                {types.map((type) => (
                    <label key={type} className="type-option">
                        <input
                            type="checkbox"
                            checked={selected.includes(type)}
                            onChange={() => onToggle(type)}
                        />
                        {type}
                    </label>
                ))}
            </div>
        </details>
    );
}

function Search() {
    const [category, setCategory] = useState("pokemon");
    const [query, setQuery] = useState("");
    const [filterValues, setFilterValues] = useState({});
    const [bounds, setBounds] = useState(null);
    const [allTypes, setAllTypes] = useState([]);
    const [selectedTypes, setSelectedTypes] = useState([]);
    const [typeMenuOpen, setTypeMenuOpen] = useState(false);

    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const { filters, typeFilter } = CATEGORIES[category];

    // Display every Pokémon when the page opens.
    useEffect(() => {
        fetchResults("pokemon", "", {}, [])
            .then(setResults)
            .catch((error) => setError(error.message))
            .finally(() => setLoading(false));
    }, []);

    // Load the min and max of every filter for the sliders.
    useEffect(() => {
        fetch("http://localhost:8000/filters")
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Could not load the filters.");
                }

                return response.json();
            })
            .then(setBounds)
            .catch((error) => setError(error.message));
    }, []);

    // Load the types for the type filter.
    useEffect(() => {
        fetch("http://localhost:8000/types")
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Could not load the types.");
                }

                return response.json();
            })
            .then(setAllTypes)
            .catch((error) => setError(error.message));
    }, []);

    function runSearch(searchCategory, searchQuery, searchFilters, searchTypes) {
        setLoading(true);
        setError(null);

        fetchResults(searchCategory, searchQuery, searchFilters, searchTypes)
            .then(setResults)
            .catch((error) => setError(error.message))
            .finally(() => setLoading(false));
    }

    function changeCategory(newCategory) {
        setCategory(newCategory);
        setFilterValues({});
        setSelectedTypes([]);
        runSearch(newCategory, query, {}, []);
    }

    function toggleType(type) {
        if (selectedTypes.includes(type)) {
            setSelectedTypes(selectedTypes.filter((selected) => selected !== type));
        } else {
            setSelectedTypes([...selectedTypes, type]);
        }
    }

    // A handle left at its bound is stored as "" so it is not sent to the backend.
    // The backend sends bounds as min_<name> / max_<name>.
    function boundsOf(name) {
        return { min: bounds[category][`min_${name}`], max: bounds[category][`max_${name}`] };
    }

    function changeFilter(name, min, max) {
        const { min: lowest, max: highest } = boundsOf(name);

        setFilterValues({
            ...filterValues,
            [`${name}_min`]: min === lowest ? "" : min,
            [`${name}_max`]: max === highest ? "" : max,
        });
    }

    function filterValue(key, bound) {
        const value = filterValues[key];
        return value === undefined || value === "" ? bound : value;
    }

    function handleSubmit(event) {
        event.preventDefault();
        setTypeMenuOpen(false);
        runSearch(category, query, filterValues, selectedTypes);
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

                    {/* Type filter */}
                    {typeFilter && (
                        <TypeFilter
                            types={allTypes}
                            selected={selectedTypes}
                            onToggle={toggleType}
                            open={typeMenuOpen}
                            onOpenChange={setTypeMenuOpen}
                        />
                    )}

                    {/* Stat filters */}
                    {bounds && filters.length > 0 && (
                        <div className="search-filters">
                            {filters.map((filter) => {
                                const filterBounds = boundsOf(filter.name);

                                return (
                                    <RangeFilter
                                        key={filter.name}
                                        label={filter.label}
                                        bounds={filterBounds}
                                        min={filterValue(`${filter.name}_min`, filterBounds.min)}
                                        max={filterValue(`${filter.name}_max`, filterBounds.max)}
                                        onChange={(min, max) => changeFilter(filter.name, min, max)}
                                    />
                                );
                            })}
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
