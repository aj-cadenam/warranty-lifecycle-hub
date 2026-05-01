from typing import Optional
from datetime import date
from src.equipos.domain.entities import Equipo, Garantia, Proveedor, TipoEquipo, EstadoEquipo, EstadoGarantia
from src.equipos.domain.ports import EquipoRepository, GarantiaRepository, ProveedorRepository
from src.equipos.infrastructure.django_models import EquipoModel, GarantiaModel, ProveedorModel


class DjangoEquipoRepository(EquipoRepository):
    def save(self, equipo: Equipo) -> None:
        EquipoModel.objects.update_or_create(
            serial=equipo.serial,
            defaults=dict(nombre=equipo.nombre, marca=equipo.marca, modelo=equipo.modelo,
                          tipo=equipo.tipo.value, ubicacion_fisica=equipo.ubicacion_fisica,
                          estado=equipo.estado.value),
        )

    def find_by_serial(self, serial: str) -> Optional[Equipo]:
        try:
            m = EquipoModel.objects.get(serial=serial)
            return self._to_entity(m)
        except EquipoModel.DoesNotExist:
            return None

    def find_all(self) -> list[Equipo]:
        return [self._to_entity(m) for m in EquipoModel.objects.all()]

    def _to_entity(self, m: EquipoModel) -> Equipo:
        return Equipo(serial=m.serial, nombre=m.nombre, marca=m.marca, modelo=m.modelo,
                      tipo=TipoEquipo(m.tipo), ubicacion_fisica=m.ubicacion_fisica,
                      estado=EstadoEquipo(m.estado))


class DjangoGarantiaRepository(GarantiaRepository):
    def save(self, garantia: Garantia) -> None:
        GarantiaModel.objects.update_or_create(
            id=int(garantia.id) if garantia.id.isdigit() else None,
            defaults=dict(equipo_serial=garantia.equipo_id, proveedor_id=1,
                          fecha_inicio=garantia.fecha_inicio, fecha_fin=garantia.fecha_fin,
                          tipo_cobertura=garantia.tipo_cobertura, estado=garantia.estado.value),
        )

    def find_vigente_by_equipo(self, equipo_id: str) -> Optional[Garantia]:
        try:
            m = GarantiaModel.objects.filter(
                equipo_serial=equipo_id, fecha_fin__gte=date.today()
            ).latest("fecha_fin")
            return Garantia(equipo_id=m.equipo_serial, proveedor_id=str(m.proveedor_id),
                            fecha_inicio=m.fecha_inicio, fecha_fin=m.fecha_fin,
                            tipo_cobertura=m.tipo_cobertura)
        except GarantiaModel.DoesNotExist:
            return None
