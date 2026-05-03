from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Accion(str, Enum):
    CREAR_SOLICITUD = "CREAR_SOLICITUD"
    ACTUALIZAR_ESTADO = "ACTUALIZAR_ESTADO"
    NOTIFICAR = "NOTIFICAR"
    ESCALAR = "ESCALAR"
    IGNORAR = "IGNORAR"


class TipoCorreo(str, Enum):
    ACTA_ENTREGA = "acta_entrega"
    ACTUALIZACION_PROVEEDOR = "actualizacion_proveedor"
    CONSULTA_CLIENTE = "consulta_cliente"
    CONFIRMACION_DESPACHO = "confirmacion_despacho"
    CONFIRMACION_DEVOLUCION = "confirmacion_devolucion"
    OTRO = "otro"


@dataclass
class DecisionAgente:
    accion: Accion
    confianza: float
    parametros: dict[str, Any] = field(default_factory=dict)
    razonamiento: str = ""


@dataclass
class CorreoEntrante:
    uid: str
    asunto: str
    cuerpo: str
    remitente: str
    adjuntos: list[str] = field(default_factory=list)  # local paths to saved attachments
    fecha: datetime = field(default_factory=datetime.now)


@dataclass
class DecisionCorreo:
    tipo: TipoCorreo
    confianza: float
    equipo_serial: str = ""
    nuevo_estado: str = ""
    tiempo_estimado_dias: int = 0
    informacion_adicional: str = ""
    razonamiento: str = ""


@dataclass
class RespuestaChat:
    respuesta: str
    accion: str = ""
    query_busqueda: str = ""
