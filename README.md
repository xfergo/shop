redis: docker compose up 

backend: uv run uvicorn main:app --reload 

frontend: uv run python -m http.server 8080
