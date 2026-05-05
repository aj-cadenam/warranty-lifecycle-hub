# api/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.database import setup_django
from config.settings import settings

# Langfuse reads os.environ directly — pydantic-settings doesn't export there
if settings.LANGFUSE_PUBLIC_KEY:
    os.environ.setdefault("LANGFUSE_PUBLIC_KEY", settings.LANGFUSE_PUBLIC_KEY)
    os.environ.setdefault("LANGFUSE_SECRET_KEY", settings.LANGFUSE_SECRET_KEY)
    os.environ.setdefault("LANGFUSE_HOST", settings.LANGFUSE_HOST)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_django()
    from config.scheduler import start, stop
    start(interval_minutes=settings.EMAIL_POLLING_INTERVAL_MINUTES)
    yield
    stop()


app = FastAPI(title="Datecsa Garantías POC", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "llm_provider": settings.LLM_PROVIDER}


def _register_routers():
    from api.routers import equipos, garantias, solicitudes, trazabilidad, borradores, agente, notificaciones
    app.include_router(equipos.router, prefix="/equipos", tags=["equipos"])
    app.include_router(garantias.router, prefix="/garantias", tags=["garantias"])
    app.include_router(solicitudes.router, prefix="/solicitudes", tags=["solicitudes"])
    app.include_router(trazabilidad.router, prefix="/trazabilidad", tags=["trazabilidad"])
    app.include_router(borradores.router, prefix="/borradores", tags=["borradores"])
    app.include_router(agente.router, prefix="/agente", tags=["agente"])
    app.include_router(notificaciones.router, prefix="/notificaciones", tags=["notificaciones"])


_register_routers()
