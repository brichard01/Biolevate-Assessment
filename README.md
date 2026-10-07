# PokéSearch

## To run the app

```sh
# 0. Configuration (no credentials, just ports)
cp .env.example .env

# 1. Database and embeddings service (first start downloads the model)
docker compose up -d

# 2. Data
curl -fL https://biolevatestatics.blob.core.windows.net/biolevate-tech-assessments/pokedex/pokedex.json \
  --create-dirs -o backend/data/pokedex.json

# 3. Backend
cd backend
conda create -n backend_pokesearch python=3.12
conda activate backend_pokesearch
pip install -r requirements.txt
python create_database.py
uvicorn main:app --port 8000

# 4. Frontend
cd frontend
npm install
npm run dev

# Tests (from backend/)
pytest
```
