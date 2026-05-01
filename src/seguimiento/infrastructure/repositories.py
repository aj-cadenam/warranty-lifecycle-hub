from typing import Optional
from src.seguimiento.domain.entities import BorradorCorreo, EventoSeguimiento, EstadoBorrador, DestinatarioTipo
from src.seguimiento.domain.ports import BorradorCorreoRepository, EventoSeguimientoRepository
from src.seguimiento.infrastructure.django_models import BorradorCorreoModel, EventoSeguimientoModel


class DjangoBorradorCorreoRepository(BorradorCorreoRepository):
    def save(self, b: BorradorCorreo) -> None:
        pk = int(b.id) if b.id.isdigit() else None
        obj, created = BorradorCorreoModel.objects.update_or_create(
            id=pk,
            defaults=dict(solicitud_id=0, destinatario_tipo=b.destinatario_tipo.value,
                          destinatario_email=b.destinatario_email, asunto=b.asunto, cuerpo=b.cuerpo,
                          estado=b.estado.value, aprobado_por=b.aprobado_por,
                          motivo_rechazo=b.motivo_rechazo, fecha_aprobacion=b.fecha_aprobacion),
        )
        if created:
            b.id = str(obj.id)

    def find_by_id(self, borrador_id: str) -> Optional[BorradorCorreo]:
        try:
            m = BorradorCorreoModel.objects.get(id=int(borrador_id))
            return self._to_entity(m)
        except (BorradorCorreoModel.DoesNotExist, ValueError):
            return None

    def find_pendientes(self) -> list[BorradorCorreo]:
        return [self._to_entity(m) for m in
                BorradorCorreoModel.objects.filter(estado=EstadoBorrador.PENDIENTE_APROBACION.value)]

    def find_by_solicitud_y_estado(self, solicitud_id: str, estado: EstadoBorrador) -> Optional[BorradorCorreo]:
        try:
            m = BorradorCorreoModel.objects.filter(solicitud_id=int(solicitud_id) if solicitud_id.isdigit() else 0,
                                                    estado=estado.value).first()
            return self._to_entity(m) if m else None
        except Exception:
            return None

    def _to_entity(self, m: BorradorCorreoModel) -> BorradorCorreo:
        b = BorradorCorreo(id=str(m.id), solicitud_id=str(m.solicitud_id),
                           destinatario_tipo=DestinatarioTipo(m.destinatario_tipo),
                           destinatario_email=m.destinatario_email, asunto=m.asunto, cuerpo=m.cuerpo,
                           estado=EstadoBorrador(m.estado), aprobado_por=m.aprobado_por,
                           motivo_rechazo=m.motivo_rechazo, fecha_aprobacion=m.fecha_aprobacion)
        return b


class DjangoEventoSeguimientoRepository(EventoSeguimientoRepository):
    def save(self, e: EventoSeguimiento) -> None:
        EventoSeguimientoModel.objects.create(
            solicitud_id=int(e.solicitud_id) if e.solicitud_id.isdigit() else 0,
            tipo_evento=e.tipo_evento, descripcion=e.descripcion,
            dias_sin_respuesta=e.dias_sin_respuesta,
        )

    def find_by_solicitud(self, solicitud_id: str) -> list[EventoSeguimiento]:
        sid = int(solicitud_id) if solicitud_id.isdigit() else 0
        return [EventoSeguimiento(solicitud_id=solicitud_id, tipo_evento=m.tipo_evento,
                                   descripcion=m.descripcion, fecha=m.fecha,
                                   dias_sin_respuesta=m.dias_sin_respuesta)
                for m in EventoSeguimientoModel.objects.filter(solicitud_id=sid)]
