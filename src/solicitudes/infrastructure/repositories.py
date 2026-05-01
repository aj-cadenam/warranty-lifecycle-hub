from typing import Optional
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.solicitudes.domain.ports import SolicitudRepository
from src.solicitudes.infrastructure.django_models import SolicitudGarantiaModel


class DjangoSolicitudRepository(SolicitudRepository):
    def save(self, solicitud: SolicitudGarantia) -> None:
        pk = int(solicitud.id) if solicitud.id.isdigit() else None
        obj, created = SolicitudGarantiaModel.objects.update_or_create(
            id=pk,
            defaults=dict(equipo_serial=solicitud.equipo_id, garantia_id=0,
                          reportado_por=solicitud.reportado_por,
                          descripcion_falla=solicitud.descripcion_falla,
                          estado=solicitud.estado.value),
        )
        if created:
            solicitud.id = str(obj.id)

    def find_by_id(self, solicitud_id: str) -> Optional[SolicitudGarantia]:
        try:
            m = SolicitudGarantiaModel.objects.get(id=int(solicitud_id))
            return self._to_entity(m)
        except (SolicitudGarantiaModel.DoesNotExist, ValueError):
            return None

    def find_by_estado(self, estado: EstadoSolicitud) -> list[SolicitudGarantia]:
        return [self._to_entity(m) for m in SolicitudGarantiaModel.objects.filter(estado=estado.value)]

    def find_all(self) -> list[SolicitudGarantia]:
        return [self._to_entity(m) for m in SolicitudGarantiaModel.objects.all()]

    def _to_entity(self, m: SolicitudGarantiaModel) -> SolicitudGarantia:
        return SolicitudGarantia(id=str(m.id), equipo_id=m.equipo_serial,
                                  garantia_id=str(m.garantia_id), reportado_por=m.reportado_por,
                                  descripcion_falla=m.descripcion_falla,
                                  fecha_reporte=m.fecha_reporte, estado=EstadoSolicitud(m.estado))
