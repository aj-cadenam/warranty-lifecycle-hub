"""FastAPI application entry point."""
from fastapi import FastAPI

app = FastAPI(
    title="Garantías Datecsa",
    version="0.1.0",
    description="API para gestión de garantías de equipos médicos.",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
