from typing import Optional
from src.trazabilidad.domain.entities import EventoTrazabilidad, MetodoRegistro
from src.trazabilidad.domain.ports import TrazabilidadRepository
from src.trazabilidad.infrastructure.django_models import EventoTrazabilidadModel


class DjangoTrazabilidadRepository(TrazabilidadRepository):
    def save(self, evento: EventoTrazabilidad) -> None:
        obj = EventoTrazabilidadModel.objects.create(
            equipo_id=evento.equipo_id,
            solicitud_id=int(evento.solicitud_id) if evento.solicitud_id.isdigit() else 0,
            ubicacion_anterior=evento.ubicacion_anterior,
            ubicacion_nueva=evento.ubicacion_nueva,
            responsable=evento.responsable,
            metodo_registro=evento.metodo_registro.value,
        )
        evento.id = str(obj.id)

    def find_by_equipo(self, equipo_id: str) -> list[EventoTrazabilidad]:
        return [
            self._to_entity(m)
            for m in EventoTrazabilidadModel.objects.filter(equipo_id=equipo_id).order_by("timestamp")
        ]

    def find_by_solicitud(self, solicitud_id: str) -> list[EventoTrazabilidad]:
        sid = int(solicitud_id) if solicitud_id.isdigit() else 0
        return [
            self._to_entity(m)
            for m in EventoTrazabilidadModel.objects.filter(solicitud_id=sid).order_by("timestamp")
        ]

    def find_ultimo_evento(self, solicitud_id: str) -> Optional[EventoTrazabilidad]:
        sid = int(solicitud_id) if solicitud_id.isdigit() else 0
        m = EventoTrazabilidadModel.objects.filter(solicitud_id=sid).order_by("-timestamp").first()
        return self._to_entity(m) if m else None

    def _to_entity(self, m: EventoTrazabilidadModel) -> EventoTrazabilidad:
        return EventoTrazabilidad(
            id=str(m.id),
            equipo_id=m.equipo_id,
            solicitud_id=str(m.solicitud_id),
            ubicacion_anterior=m.ubicacion_anterior,
            ubicacion_nueva=m.ubicacion_nueva,
            responsable=m.responsable,
            timestamp=m.timestamp,
            metodo_registro=MetodoRegistro(m.metodo_registro),
        )
