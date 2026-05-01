from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def agente_health():
    return {"status": "agente ok"}
