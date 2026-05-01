from src.seguimiento.domain.ports import BorradorCorreoRepository


class RechazarBorrador:
    def __init__(self, borrador_repo: BorradorCorreoRepository):
        self._repo = borrador_repo

    def execute(self, borrador_id: str, motivo: str) -> None:
        borrador = self._repo.find_by_id(borrador_id)
        if borrador is None:
            raise ValueError(f"borrador {borrador_id} no encontrado")
        borrador.rechazar(motivo=motivo)
        self._repo.save(borrador)
