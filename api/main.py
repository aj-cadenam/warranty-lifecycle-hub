# api/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.database import setup_django


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_django()
    yield


app = FastAPI(title="Datecsa Garantías POC", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


def _register_routers():
    from api.routers import equipos, solicitudes, borradores, agente, notificaciones
    app.include_router(equipos.router, prefix="/equipos", tags=["equipos"])
    app.include_router(solicitudes.router, prefix="/solicitudes", tags=["solicitudes"])
    app.include_router(borradores.router, prefix="/borradores", tags=["borradores"])
    app.include_router(agente.router, prefix="/agente", tags=["agente"])
    app.include_router(notificaciones.router, prefix="/notificaciones", tags=["notificaciones"])


_register_routers()
