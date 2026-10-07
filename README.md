# PokéSearch

## To run the app

0. Configuration (no credentials, just ports)

```sh
cp .env.example .env
```

1. Database and embeddings service (first start downloads the model)

```sh
docker compose up -d
```

2. Data

```sh
curl -fL https://biolevatestatics.blob.core.windows.net/biolevate-tech-assessments/pokedex/pokedex.json \
  --create-dirs -o backend/data/pokedex.json
```

3. Backend

```sh
cd backend
conda create -n backend_pokesearch python=3.12
conda activate backend_pokesearch
pip install -r requirements.txt
python create_database.py
uvicorn main:app --port 8000
```

4. Frontend

```sh
cd frontend
npm install
npm run dev
```

Tests (from backend/)

```sh
pytest
```
