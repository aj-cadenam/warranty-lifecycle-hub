from src.solicitudes.domain.entities import SolicitudGarantia
from src.solicitudes.domain.ports import SolicitudRepository
from src.equipos.domain.ports import GarantiaRepository


class CrearSolicitud:
    def __init__(self, solicitud_repo: SolicitudRepository, garantia_repo: GarantiaRepository):
        self._solicitud_repo = solicitud_repo
        self._garantia_repo = garantia_repo

    def execute(self, equipo_id: str, reportado_por: str, descripcion_falla: str) -> SolicitudGarantia:
        garantia = self._garantia_repo.find_vigente_by_equipo(equipo_id)
        if garantia is None:
            raise ValueError(f"equipo {equipo_id} no tiene garantía vigente")
        solicitud = SolicitudGarantia(equipo_id=equipo_id, garantia_id=garantia.id,
                                      reportado_por=reportado_por, descripcion_falla=descripcion_falla)
        self._solicitud_repo.save(solicitud)
        return solicitud
