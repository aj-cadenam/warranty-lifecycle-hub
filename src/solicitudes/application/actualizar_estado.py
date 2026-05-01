from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.solicitudes.domain.ports import SolicitudRepository


class ActualizarEstado:
    def __init__(self, solicitud_repo: SolicitudRepository):
        self._repo = solicitud_repo

    def execute(self, solicitud_id: str, nuevo_estado: EstadoSolicitud) -> SolicitudGarantia:
        solicitud = self._repo.find_by_id(solicitud_id)
        if solicitud is None:
            raise ValueError(f"solicitud {solicitud_id} no encontrada")
        _METODOS = {
            EstadoSolicitud.VALIDADA: solicitud.validar,
            EstadoSolicitud.DESPACHADA: solicitud.despachar,
        }
        metodo = _METODOS.get(nuevo_estado)
        if metodo is None:
            raise ValueError(f"transición a {nuevo_estado} no soportada vía este endpoint")
        metodo()
        self._repo.save(solicitud)
        return solicitud
