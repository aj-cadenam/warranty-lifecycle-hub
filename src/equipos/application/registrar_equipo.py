from src.equipos.domain.entities import Equipo, TipoEquipo
from src.equipos.domain.ports import EquipoRepository


class RegistrarEquipo:
    def __init__(self, equipo_repo: EquipoRepository):
        self._repo = equipo_repo

    def execute(self, serial: str, nombre: str, marca: str, modelo: str,
                tipo: TipoEquipo, ubicacion_fisica: str) -> Equipo:
        if self._repo.find_by_serial(serial) is not None:
            raise ValueError(f"serial ya existe: {serial}")
        equipo = Equipo(serial=serial, nombre=nombre, marca=marca, modelo=modelo,
                        tipo=tipo, ubicacion_fisica=ubicacion_fisica)
        self._repo.save(equipo)
        return equipo
