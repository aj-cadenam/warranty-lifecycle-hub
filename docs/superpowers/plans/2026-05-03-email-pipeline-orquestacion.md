# Pipeline Orquestación de Correos — Flujo Multi-destinatario

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When a new email arrives at `garantias_mock@outlook.com`, an orchestrator agent creates trazabilidad events and generates draft emails for ALL relevant recipients (responsable, bodega, despacho, recepción, proveedor) based on the email type and current case state — completing the full warranty loop automatically with human-in-the-loop approval before sending.

**Architecture:** New `OrquestarAcciones` use case maps `TipoCorreo` → set of `BorradorCorreo` for different `DestinatarioTipo` values. Called from `ProcesarCorreo` after classification + trazabilidad update. Internal contact emails live in `config/settings.py`. `dias_sin_respuesta` is added to `BorradorCorreo` entity and DB model so follow-up drafts carry context. Gemini `classify_email` prompt is updated to recognize the new `confirmacion_devolucion` event type.

**Tech Stack:** Python, FastAPI, Django ORM, hexagonal architecture, FakeLLM/FakeEmail adapters for tests.

---

## Email Flow After This Plan

```
Email arrives at garantias_mock@outlook.com
        ↓
OutlookIMAPAdapter.fetch_unread()
        ↓
GeminiLLMAdapter.classify_email(asunto, cuerpo)
        ↓ TipoCorreo
┌──────────────────────────────────────────────────────┐
│ ACTA_ENTREGA        → crea solicitud                 │
│                     → borrador para RESPONSABLE       │
│                                                      │
│ ACTUALIZACION_PROVEEDOR → actualiza estado           │
│                          → borrador para RESPONSABLE  │
│                                                      │
│ CONFIRMACION_DESPACHO → estado: en_reparacion        │
│  (proveedor confirma  → borrador para RESPONSABLE    │
│   que recibió equipo) → (sin bodega/despacho aún)    │
│                                                      │
│ CONFIRMACION_DEVOLUCION → estado: devuelta           │
│  (proveedor envía equipo → borrador para BODEGA      │
│   de vuelta al cliente)  → borrador para DESPACHO    │
│                           → borrador para RECEPCION  │
│                           → borrador para RESPONSABLE │
│                                                      │
│ CONSULTA_CLIENTE → borrador para RESPONSABLE         │
└──────────────────────────────────────────────────────┘
        ↓
Usuario revisa y aprueba borradores en UI
        ↓
EmailAdapter.send() → correo sale del sistema
```

---

## File Map

| File | Change |
|------|--------|
| `src/agente/domain/entities.py` | + `CONFIRMACION_DEVOLUCION` a `TipoCorreo` |
| `src/seguimiento/domain/entities.py` | + `RESPONSABLE,BODEGA,DESPACHO,RECEPCION` en `DestinatarioTipo` + `dias_sin_respuesta: int = 0` en `BorradorCorreo` |
| `src/agente/application/orquestar_acciones.py` | **NUEVO** — routing logic |
| `src/agente/application/procesar_correo.py` | integrar `OrquestarAcciones`, fix return types de `_manejar_*` |
| `src/seguimiento/application/verificar_estado_semanal.py` | pasar `dias_sin_respuesta` al crear borradores |
| `src/seguimiento/infrastructure/django_models.py` | + columna `dias_sin_respuesta` |
| `src/seguimiento/infrastructure/repositories.py` | persist/load `dias_sin_respuesta` |
| `src/seguimiento/infrastructure/migrations/0002_borrador_dias_sin_respuesta.py` | **NUEVO** — migración |
| `src/agente/infrastructure/email/fake_email_adapter.py` | + 2 escenarios (confirmacion_despacho, confirmacion_devolucion) |
| `src/agente/infrastructure/llm/fake_llm_adapter.py` | + clasificación `CONFIRMACION_DEVOLUCION` |
| `src/agente/infrastructure/llm/gemini_llm_adapter.py` | actualizar prompt de `classify_email` |
| `config/settings.py` | + 4 emails de contactos internos |
| `config/dependencies.py` | + `get_orquestar_acciones()` |
| `config/scheduler.py` | pasar `OrquestarAcciones` a `ProcesarCorreo` |
| `api/routers/agente.py` | pasar `OrquestarAcciones` en endpoint `procesar_correos` |
| `api/routers/borradores.py` | + `destinatario_tipo` + `dias_sin_respuesta` + `fecha_aprobacion` en `BorradorResponse` |
| `frontend/src/types/index.ts` | + `destinatario_tipo` + `dias_sin_respuesta` + `fecha_aprobacion` en `BorradorCorreo` |

---

## Task 1: Expandir entidades de dominio

**Files:**
- Modify: `src/agente/domain/entities.py`
- Modify: `src/seguimiento/domain/entities.py`
- Test: `tests/unit/test_domain_entities.py`

- [ ] **Step 1: Escribir los tests que fallan**

```python
# tests/unit/test_domain_entities.py
from src.agente.domain.entities import TipoCorreo
from src.seguimiento.domain.entities import DestinatarioTipo, BorradorCorreo


def test_tipo_correo_tiene_confirmacion_devolucion():
    assert TipoCorreo.CONFIRMACION_DEVOLUCION == "confirmacion_devolucion"


def test_destinatario_tipo_tiene_internos():
    assert DestinatarioTipo.RESPONSABLE == "responsable"
    assert DestinatarioTipo.BODEGA == "bodega"
    assert DestinatarioTipo.DESPACHO == "despacho"
    assert DestinatarioTipo.RECEPCION == "recepcion"


def test_borrador_correo_tiene_dias_sin_respuesta():
    b = BorradorCorreo()
    assert b.dias_sin_respuesta == 0


def test_borrador_correo_acepta_dias_sin_respuesta():
    b = BorradorCorreo(dias_sin_respuesta=12)
    assert b.dias_sin_respuesta == 12
```

- [ ] **Step 2: Correr tests para verificar que fallan**

```bash
uv run pytest tests/unit/test_domain_entities.py -v
```

Expected: FAIL con `AttributeError: CONFIRMACION_DEVOLUCION` y `AttributeError: RESPONSABLE`

- [ ] **Step 3: Actualizar `src/agente/domain/entities.py`**

Localizar la clase `TipoCorreo` y agregar el nuevo valor:

```python
class TipoCorreo(str, Enum):
    ACTA_ENTREGA = "acta_entrega"
    ACTUALIZACION_PROVEEDOR = "actualizacion_proveedor"
    CONSULTA_CLIENTE = "consulta_cliente"
    CONFIRMACION_DESPACHO = "confirmacion_despacho"
    CONFIRMACION_DEVOLUCION = "confirmacion_devolucion"
    OTRO = "otro"
```

- [ ] **Step 4: Actualizar `src/seguimiento/domain/entities.py`**

Reemplazar `DestinatarioTipo` y agregar `dias_sin_respuesta` a `BorradorCorreo`:

```python
class DestinatarioTipo(str, Enum):
    PROVEEDOR = "proveedor"
    CLIENTE = "cliente"
    RESPONSABLE = "responsable"
    BODEGA = "bodega"
    DESPACHO = "despacho"
    RECEPCION = "recepcion"


@dataclass
class BorradorCorreo(BaseEntity):
    solicitud_id: str = ""
    destinatario_tipo: DestinatarioTipo = DestinatarioTipo.PROVEEDOR
    destinatario_email: str = ""
    asunto: str = ""
    cuerpo: str = ""
    estado: EstadoBorrador = EstadoBorrador.PENDIENTE_APROBACION
    aprobado_por: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    fecha_aprobacion: Optional[datetime] = None
    dias_sin_respuesta: int = 0

    def aprobar(self, aprobado_por: str) -> None:
        if self.estado == EstadoBorrador.ENVIADO:
            raise ValueError("ya fue enviado")
        if self.estado == EstadoBorrador.RECHAZADO:
            raise ValueError("fue rechazado")
        self.estado = EstadoBorrador.APROBADO
        self.aprobado_por = aprobado_por
        self.fecha_aprobacion = datetime.now()

    def rechazar(self, motivo: str) -> None:
        self.estado = EstadoBorrador.RECHAZADO
        self.motivo_rechazo = motivo

    def marcar_enviado(self) -> None:
        if self.estado != EstadoBorrador.APROBADO:
            raise ValueError("no está aprobado para envío")
        self.estado = EstadoBorrador.ENVIADO
```

- [ ] **Step 5: Correr tests para verificar que pasan**

```bash
uv run pytest tests/unit/test_domain_entities.py -v
```

Expected: 4 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/agente/domain/entities.py src/seguimiento/domain/entities.py tests/unit/test_domain_entities.py
git commit -m "feat: expand TipoCorreo and DestinatarioTipo, add dias_sin_respuesta to BorradorCorreo"
```

---

## Task 2: Use case `OrquestarAcciones`

**Files:**
- Create: `src/agente/application/orquestar_acciones.py`
- Create: `tests/application/test_orquestar_acciones.py`

- [ ] **Step 1: Escribir los tests que fallan**

```python
# tests/application/test_orquestar_acciones.py
from src.agente.application.orquestar_acciones import OrquestarAcciones
from src.agente.domain.entities import TipoCorreo, DecisionCorreo
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter
from src.seguimiento.domain.entities import DestinatarioTipo, EstadoBorrador
from src.seguimiento.domain.ports import BorradorCorreoRepository
from src.solicitudes.domain.entities import SolicitudGarantia
from typing import Optional


class InMemoryBorradorRepo(BorradorCorreoRepository):
    def __init__(self):
        self._store: list = []
    def save(self, b):
        self._store.append(b)
    def find_by_id(self, id_): return None
    def find_pendientes(self): return list(self._store)
    def find_by_solicitud_y_estado(self, sid, estado): return None


def _solicitud(equipo_id: str = "KYO-001") -> SolicitudGarantia:
    return SolicitudGarantia(
        id="sol-1",
        equipo_id=equipo_id,
        reportado_por="Agente Test",
        descripcion_falla="Error fusor",
    )


def _decision(tipo: TipoCorreo, serial: str = "KYO-001") -> DecisionCorreo:
    return DecisionCorreo(tipo=tipo, confianza=0.95, equipo_serial=serial)


def test_acta_entrega_notifica_responsable():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=repo,
        responsable_email="resp@datecsa.com",
    )
    borradores = uc.execute(_solicitud(), _decision(TipoCorreo.ACTA_ENTREGA))
    assert len(borradores) == 1
    assert borradores[0].destinatario_tipo == DestinatarioTipo.RESPONSABLE
    assert borradores[0].destinatario_email == "resp@datecsa.com"
    assert borradores[0].estado == EstadoBorrador.PENDIENTE_APROBACION


def test_actualizacion_proveedor_notifica_responsable():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=repo,
        responsable_email="resp@datecsa.com",
    )
    borradores = uc.execute(_solicitud(), _decision(TipoCorreo.ACTUALIZACION_PROVEEDOR))
    assert len(borradores) == 1
    assert borradores[0].destinatario_tipo == DestinatarioTipo.RESPONSABLE


def test_confirmacion_devolucion_notifica_bodega_despacho_recepcion_responsable():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=repo,
        responsable_email="resp@datecsa.com",
        bodega_email="bodega@datecsa.com",
        despacho_email="despacho@datecsa.com",
        recepcion_email="recepcion@datecsa.com",
    )
    borradores = uc.execute(_solicitud(), _decision(TipoCorreo.CONFIRMACION_DEVOLUCION))
    tipos = {b.destinatario_tipo for b in borradores}
    assert len(borradores) == 4
    assert DestinatarioTipo.BODEGA in tipos
    assert DestinatarioTipo.DESPACHO in tipos
    assert DestinatarioTipo.RECEPCION in tipos
    assert DestinatarioTipo.RESPONSABLE in tipos


def test_sin_emails_configurados_no_crea_borradores():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(llm=FakeLLMAdapter(), borrador_repo=repo)
    borradores = uc.execute(_solicitud(), _decision(TipoCorreo.CONFIRMACION_DEVOLUCION))
    assert len(borradores) == 0


def test_tipo_otro_no_crea_borradores():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=repo,
        responsable_email="resp@datecsa.com",
    )
    borradores = uc.execute(_solicitud(), _decision(TipoCorreo.OTRO))
    assert len(borradores) == 0


def test_borradores_son_persistidos():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=repo,
        responsable_email="resp@datecsa.com",
    )
    uc.execute(_solicitud(), _decision(TipoCorreo.ACTA_ENTREGA))
    assert len(repo._store) == 1
    assert repo._store[0].solicitud_id == "sol-1"
```

- [ ] **Step 2: Correr tests para verificar que fallan**

```bash
uv run pytest tests/application/test_orquestar_acciones.py -v
```

Expected: FAIL con `ModuleNotFoundError: No module named 'src.agente.application.orquestar_acciones'`

- [ ] **Step 3: Crear `src/agente/application/orquestar_acciones.py`**

```python
from dataclasses import dataclass
from src.agente.domain.entities import TipoCorreo, DecisionCorreo
from src.agente.domain.ports import LLMPort
from src.seguimiento.domain.entities import BorradorCorreo, DestinatarioTipo
from src.seguimiento.domain.ports import BorradorCorreoRepository
from src.solicitudes.domain.entities import SolicitudGarantia


@dataclass
class _Destino:
    tipo: DestinatarioTipo
    email: str
    rol_label: str


class OrquestarAcciones:
    def __init__(
        self,
        llm: LLMPort,
        borrador_repo: BorradorCorreoRepository,
        responsable_email: str = "",
        bodega_email: str = "",
        despacho_email: str = "",
        recepcion_email: str = "",
    ):
        self._llm = llm
        self._repo = borrador_repo
        self._responsable = responsable_email
        self._bodega = bodega_email
        self._despacho = despacho_email
        self._recepcion = recepcion_email

    def execute(
        self,
        solicitud: SolicitudGarantia,
        decision: DecisionCorreo,
    ) -> list[BorradorCorreo]:
        destinos = self._resolver_destinos(decision.tipo)
        borradores: list[BorradorCorreo] = []
        for dest in destinos:
            contexto = (
                f"Solicitud {solicitud.id}, equipo {solicitud.equipo_id}. "
                f"Falla: {solicitud.descripcion_falla}. "
                f"Evento recibido: {decision.tipo.value}. "
                f"Información adicional: {decision.informacion_adicional}. "
                f"Destinatario: {dest.rol_label}."
            )
            email_data = self._llm.generate_email(contexto)
            borrador = BorradorCorreo(
                solicitud_id=solicitud.id,
                destinatario_tipo=dest.tipo,
                destinatario_email=dest.email,
                asunto=email_data["asunto"],
                cuerpo=email_data["cuerpo"],
            )
            self._repo.save(borrador)
            borradores.append(borrador)
        return borradores

    def _resolver_destinos(self, tipo: TipoCorreo) -> list[_Destino]:
        destinos: list[_Destino] = []

        def add(tipo_dest: DestinatarioTipo, email: str, label: str) -> None:
            if email:
                destinos.append(_Destino(tipo=tipo_dest, email=email, rol_label=label))

        if tipo == TipoCorreo.ACTA_ENTREGA:
            add(DestinatarioTipo.RESPONSABLE, self._responsable, "Responsable de garantías")

        elif tipo == TipoCorreo.ACTUALIZACION_PROVEEDOR:
            add(DestinatarioTipo.RESPONSABLE, self._responsable, "Responsable de garantías")

        elif tipo == TipoCorreo.CONFIRMACION_DESPACHO:
            add(DestinatarioTipo.RESPONSABLE, self._responsable, "Responsable de garantías")

        elif tipo == TipoCorreo.CONFIRMACION_DEVOLUCION:
            add(DestinatarioTipo.BODEGA, self._bodega, "Bodega")
            add(DestinatarioTipo.DESPACHO, self._despacho, "Despacho")
            add(DestinatarioTipo.RECEPCION, self._recepcion, "Recepción")
            add(DestinatarioTipo.RESPONSABLE, self._responsable, "Responsable de garantías")

        elif tipo == TipoCorreo.CONSULTA_CLIENTE:
            add(DestinatarioTipo.RESPONSABLE, self._responsable, "Responsable de garantías")

        return destinos
```

- [ ] **Step 4: Correr tests para verificar que pasan**

```bash
uv run pytest tests/application/test_orquestar_acciones.py -v
```

Expected: 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/agente/application/orquestar_acciones.py tests/application/test_orquestar_acciones.py
git commit -m "feat: add OrquestarAcciones use case for multi-recipient email routing"
```

---

## Task 3: Integrar `OrquestarAcciones` en `ProcesarCorreo`

**Files:**
- Modify: `src/agente/application/procesar_correo.py`
- Test: `tests/application/test_procesar_correo_orquestado.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/application/test_procesar_correo_orquestado.py
from datetime import datetime
from src.agente.application.procesar_correo import ProcesarCorreo
from src.agente.application.orquestar_acciones import OrquestarAcciones
from src.agente.domain.entities import CorreoEntrante
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter
from src.agente.infrastructure.email.fake_email_adapter import FakeEmailReaderAdapter, FakeEmailAdapter
from src.agente.infrastructure.ocr.fake_ocr_adapter import FakeOCRAdapter
from src.agente.infrastructure.embeddings.fake_embedding_adapter import FakeEmbeddingAdapter
from src.seguimiento.domain.entities import DestinatarioTipo
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.solicitudes.domain.ports import SolicitudRepository
from src.trazabilidad.domain.ports import TrazabilidadRepository
from src.seguimiento.domain.ports import BorradorCorreoRepository
from src.solicitudes.application.crear_solicitud import CrearSolicitud
from src.equipos.domain.entities import Equipo, Garantia, TipoEquipo
from datetime import date
from typing import Optional


# ── Fakes ──

class FakeVectorStore:
    def store(self, chunks, embeddings): pass
    def search(self, emb, limit=5): return []


class FakeSolicitudRepo(SolicitudRepository):
    def __init__(self):
        self._store: dict[str, SolicitudGarantia] = {}
        self._id_counter = 1

    def save(self, s: SolicitudGarantia) -> None:
        if not s.id:
            s.id = str(self._id_counter)
            self._id_counter += 1
        self._store[s.id] = s

    def find_by_id(self, id_: str) -> Optional[SolicitudGarantia]:
        return self._store.get(id_)

    def find_all(self) -> list[SolicitudGarantia]:
        return list(self._store.values())

    def find_by_estado(self, estado: EstadoSolicitud) -> list[SolicitudGarantia]:
        return [s for s in self._store.values() if s.estado == estado]


class FakeGarantiaRepo:
    def find_vigente_by_equipo(self, equipo_id: str) -> Optional[Garantia]:
        return Garantia(
            equipo_id=equipo_id,
            proveedor_id="prov-1",
            fecha_inicio=date(2020, 1, 1),
            fecha_fin=date(2027, 1, 1),
            tipo_cobertura="total",
        )
    def save(self, g): pass


class FakeTrazabilidadRepo(TrazabilidadRepository):
    def __init__(self):
        self._store = []
    def save(self, e): self._store.append(e)
    def find_by_equipo(self, eid): return []
    def find_by_solicitud(self, sid): return []
    def find_ultimo_evento(self, sid): return None


class InMemoryBorradorRepo(BorradorCorreoRepository):
    def __init__(self):
        self._store = []
    def save(self, b): self._store.append(b)
    def find_by_id(self, id_): return None
    def find_pendientes(self): return list(self._store)
    def find_by_solicitud_y_estado(self, sid, estado): return None


# ── Tests ──

def _inbox_with(correos: list[CorreoEntrante]) -> FakeEmailReaderAdapter:
    return FakeEmailReaderAdapter(correos=correos)


def test_acta_entrega_genera_borrador_responsable():
    inbox = _inbox_with([CorreoEntrante(
        uid="t-001",
        asunto="Acta de entrega - KYO-TASKalfa-2021-001",
        cuerpo="Falla error fusor C3100. Serial: KYO-TASKalfa-2021-001.",
        remitente="tecnico@datecsa.com",
        fecha=datetime.now(),
    )])
    solicitud_repo = FakeSolicitudRepo()
    borrador_repo = InMemoryBorradorRepo()
    orquestar = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=borrador_repo,
        responsable_email="resp@datecsa.com",
    )
    caso_uso = ProcesarCorreo(
        llm=FakeLLMAdapter(),
        email_reader=inbox,
        ocr=FakeOCRAdapter(),
        embedding=FakeEmbeddingAdapter(dim=768),
        vector_store=FakeVectorStore(),
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=FakeTrazabilidadRepo(),
        crear_solicitud=CrearSolicitud(
            solicitud_repo=solicitud_repo,
            garantia_repo=FakeGarantiaRepo(),
        ),
        orquestar=orquestar,
    )
    result = caso_uso.execute()
    assert result["procesados"] == 1
    assert result["detalle"][0]["borradores_generados"] == 1
    assert result["detalle"][0]["destinatarios"] == ["responsable"]


def test_confirmacion_devolucion_genera_4_borradores():
    inbox = _inbox_with([CorreoEntrante(
        uid="t-002",
        asunto="Equipo reparado listo para retiro - KYO-TASKalfa-2021-001",
        cuerpo="El equipo serial KYO-TASKalfa-2021-001 está listo para retiro.",
        remitente="soporte@kyocera.com",
        fecha=datetime.now(),
    )])
    solicitud_repo = FakeSolicitudRepo()
    # Pre-load a solicitud in despachada state
    sol = SolicitudGarantia(
        id="sol-existing",
        equipo_id="KYO-TASKalfa-2021-001",
        reportado_por="Test",
        descripcion_falla="Error fusor",
        estado=EstadoSolicitud.DESPACHADA,
    )
    solicitud_repo.save(sol)

    borrador_repo = InMemoryBorradorRepo()
    orquestar = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=borrador_repo,
        responsable_email="resp@datecsa.com",
        bodega_email="bodega@datecsa.com",
        despacho_email="despacho@datecsa.com",
        recepcion_email="recepcion@datecsa.com",
    )
    caso_uso = ProcesarCorreo(
        llm=FakeLLMAdapter(),
        email_reader=inbox,
        ocr=FakeOCRAdapter(),
        embedding=FakeEmbeddingAdapter(dim=768),
        vector_store=FakeVectorStore(),
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=FakeTrazabilidadRepo(),
        crear_solicitud=CrearSolicitud(
            solicitud_repo=solicitud_repo,
            garantia_repo=FakeGarantiaRepo(),
        ),
        orquestar=orquestar,
    )
    result = caso_uso.execute()
    assert result["detalle"][0]["borradores_generados"] == 4
```

- [ ] **Step 2: Correr tests para verificar que fallan**

```bash
uv run pytest tests/application/test_procesar_correo_orquestado.py -v
```

Expected: FAIL — `ProcesarCorreo.__init__()` no acepta `orquestar`, y `result["detalle"][0]` no tiene `borradores_generados`

- [ ] **Step 3: Actualizar `src/agente/application/procesar_correo.py`**

Reemplazar el archivo completo:

```python
from typing import Optional, Tuple
from langfuse import observe
from src.agente.domain.entities import CorreoEntrante, DecisionCorreo, TipoCorreo
from src.agente.domain.ports import LLMPort, EmailReaderPort, OCRPort, EmbeddingPort, VectorStorePort
from src.agente.application.procesar_documento import ProcesarDocumento
from src.solicitudes.application.actualizar_estado import ActualizarEstado
from src.solicitudes.domain.entities import EstadoSolicitud, SolicitudGarantia
from src.solicitudes.domain.ports import SolicitudRepository
from src.trazabilidad.domain.entities import EventoTrazabilidad, MetodoRegistro
from src.trazabilidad.domain.ports import TrazabilidadRepository
from src.solicitudes.application.crear_solicitud import CrearSolicitud

_ESTADO_MAP: dict[str, EstadoSolicitud] = {
    "validada": EstadoSolicitud.VALIDADA,
    "despachada": EstadoSolicitud.DESPACHADA,
    "en_reparacion": EstadoSolicitud.EN_REPARACION,
    "devuelta": EstadoSolicitud.DEVUELTA,
    "cerrada": EstadoSolicitud.CERRADA,
}


class ProcesarCorreo:
    def __init__(
        self,
        llm: LLMPort,
        email_reader: EmailReaderPort,
        ocr: OCRPort,
        embedding: EmbeddingPort,
        vector_store: VectorStorePort,
        solicitud_repo: SolicitudRepository,
        trazabilidad_repo: TrazabilidadRepository,
        crear_solicitud: CrearSolicitud,
        orquestar=None,  # OrquestarAcciones | None — optional to keep backwards compat
    ):
        self._llm = llm
        self._email_reader = email_reader
        self._ocr = ocr
        self._embedding = embedding
        self._vector_store = vector_store
        self._solicitud_repo = solicitud_repo
        self._trazabilidad_repo = trazabilidad_repo
        self._crear_solicitud = crear_solicitud
        self._orquestar = orquestar

    @observe(name="procesar_correos")
    def execute(self) -> dict:
        correos = self._email_reader.fetch_unread()
        resultados = []
        for correo in correos:
            resultado = self._procesar(correo)
            self._email_reader.mark_as_read(correo.uid)
            resultados.append(resultado)
        return {"procesados": len(resultados), "detalle": resultados}

    def _procesar(self, correo: CorreoEntrante) -> dict:
        decision = self._llm.classify_email(correo.asunto, correo.cuerpo)
        resultado: dict = {
            "uid": correo.uid,
            "asunto": correo.asunto,
            "remitente": correo.remitente,
            "tipo": decision.tipo.value,
            "confianza": decision.confianza,
            "equipo_serial": decision.equipo_serial,
            "accion_tomada": None,
            "borradores_generados": 0,
            "destinatarios": [],
        }

        solicitud: Optional[SolicitudGarantia] = None

        if decision.tipo == TipoCorreo.ACTA_ENTREGA:
            accion, solicitud = self._manejar_acta(correo, decision)
            resultado["accion_tomada"] = accion

        elif decision.tipo in (
            TipoCorreo.ACTUALIZACION_PROVEEDOR,
            TipoCorreo.CONFIRMACION_DESPACHO,
            TipoCorreo.CONFIRMACION_DEVOLUCION,
        ):
            accion, solicitud = self._manejar_actualizacion(correo, decision)
            resultado["accion_tomada"] = accion

        elif decision.tipo == TipoCorreo.CONSULTA_CLIENTE:
            resultado["accion_tomada"] = "consulta_registrada"
            if decision.equipo_serial:
                todas = (
                    self._solicitud_repo.find_by_estado(EstadoSolicitud.NUEVA)
                    + self._solicitud_repo.find_by_estado(EstadoSolicitud.VALIDADA)
                    + self._solicitud_repo.find_by_estado(EstadoSolicitud.DESPACHADA)
                    + self._solicitud_repo.find_by_estado(EstadoSolicitud.EN_REPARACION)
                )
                solicitud = next((s for s in todas if s.equipo_id == decision.equipo_serial), None)

        else:
            resultado["accion_tomada"] = "ignorado"

        if self._orquestar and solicitud:
            borradores = self._orquestar.execute(solicitud=solicitud, decision=decision)
            resultado["borradores_generados"] = len(borradores)
            resultado["destinatarios"] = [b.destinatario_tipo.value for b in borradores]

        return resultado

    def _manejar_acta(
        self, correo: CorreoEntrante, decision: DecisionCorreo
    ) -> Tuple[str, Optional[SolicitudGarantia]]:
        for pdf_path in correo.adjuntos:
            procesador = ProcesarDocumento(
                ocr=self._ocr,
                llm=self._llm,
                embedding=self._embedding,
                vector_store=self._vector_store,
                crear_solicitud=self._crear_solicitud,
            )
            _, solicitud = procesador.execute(pdf_path=pdf_path)
            return "solicitud_creada_desde_pdf", solicitud

        if decision.equipo_serial:
            try:
                solicitud = self._crear_solicitud.execute(
                    equipo_id=decision.equipo_serial,
                    reportado_por=correo.remitente,
                    descripcion_falla=correo.cuerpo[:500],
                )
                return "solicitud_creada_desde_correo", solicitud
            except ValueError:
                return "equipo_sin_garantia_vigente", None
        return "sin_serial_identificado", None

    def _manejar_actualizacion(
        self, correo: CorreoEntrante, decision: DecisionCorreo
    ) -> Tuple[str, Optional[SolicitudGarantia]]:
        if not decision.equipo_serial:
            return "sin_serial_identificado", None

        solicitudes = (
            self._solicitud_repo.find_by_estado(EstadoSolicitud.DESPACHADA)
            + self._solicitud_repo.find_by_estado(EstadoSolicitud.EN_REPARACION)
        )
        solicitud = next((s for s in solicitudes if s.equipo_id == decision.equipo_serial), None)

        if not solicitud:
            return "solicitud_activa_no_encontrada", None

        nuevo_estado = _ESTADO_MAP.get(decision.nuevo_estado)
        if nuevo_estado:
            ActualizarEstado(self._solicitud_repo).execute(solicitud.id, nuevo_estado)

        evento = EventoTrazabilidad(
            equipo_id=decision.equipo_serial,
            solicitud_id=solicitud.id,
            ubicacion_anterior=solicitud.estado.value,
            ubicacion_nueva=decision.nuevo_estado or "actualizado_por_proveedor",
            responsable=correo.remitente,
            metodo_registro=MetodoRegistro.AGENTE_EMAIL,
            notas=decision.informacion_adicional,
            tiempo_estimado_dias=decision.tiempo_estimado_dias,
        )
        self._trazabilidad_repo.save(evento)
        return "estado_actualizado", solicitud
```

- [ ] **Step 4: Correr tests para verificar que pasan**

```bash
uv run pytest tests/application/test_procesar_correo_orquestado.py -v
```

Expected: 2 tests PASS

- [ ] **Step 5: Asegurarse de que los tests existentes no se rompieron**

```bash
uv run pytest tests/application/ tests/unit/ -v
```

Expected: todos PASS

- [ ] **Step 6: Commit**

```bash
git add src/agente/application/procesar_correo.py tests/application/test_procesar_correo_orquestado.py
git commit -m "feat: integrate OrquestarAcciones into ProcesarCorreo, fix return types"
```

---

## Task 4: Corregir `VerificarEstadoSemanal` — set `dias_sin_respuesta`

**Files:**
- Modify: `src/seguimiento/application/verificar_estado_semanal.py`

`VerificarEstadoSemanal` genera borradores de seguimiento pero no pasa `dias_sin_respuesta`. Los borradores así no muestran en la UI cuántos días lleva sin respuesta.

- [ ] **Step 1: Escribir test que falla**

```python
# tests/application/test_verificar_estado_semanal_dias.py
from datetime import datetime, timedelta
from src.seguimiento.application.verificar_estado_semanal import VerificarEstadoSemanal
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.trazabilidad.domain.entities import EventoTrazabilidad
from src.solicitudes.domain.ports import SolicitudRepository
from src.trazabilidad.domain.ports import TrazabilidadRepository
from src.seguimiento.domain.ports import BorradorCorreoRepository, EventoSeguimientoRepository
from src.seguimiento.domain.entities import EstadoBorrador
from typing import Optional


class FakeSolicitudRepoVS:
    def find_by_estado(self, estado):
        if estado == EstadoSolicitud.DESPACHADA:
            return [SolicitudGarantia(
                id="sol-1", equipo_id="KYO-001",
                reportado_por="Test", descripcion_falla="Falla",
                estado=EstadoSolicitud.DESPACHADA,
            )]
        return []
    def find_all(self): return []
    def save(self, s): pass
    def find_by_id(self, id_): return None


class FakeTrazabilidadRepoVS:
    def __init__(self, dias_atras: int):
        self._dias = dias_atras
    def find_ultimo_evento(self, sid):
        return EventoTrazabilidad(
            solicitud_id=sid,
            equipo_id="KYO-001",
            timestamp=datetime.now() - timedelta(days=self._dias),
        )
    def find_by_equipo(self, eid): return []
    def find_by_solicitud(self, sid): return []
    def save(self, e): pass


class InMemBorradorRepoVS:
    def __init__(self):
        self._store = []
    def save(self, b): self._store.append(b)
    def find_by_id(self, id_): return None
    def find_pendientes(self): return list(self._store)
    def find_by_solicitud_y_estado(self, sid, estado): return None


class InMemSeguimientoRepo:
    def save(self, e): pass
    def find_by_solicitud(self, sid): return []


def test_borrador_tiene_dias_sin_respuesta():
    borrador_repo = InMemBorradorRepoVS()
    uc = VerificarEstadoSemanal(
        solicitud_repo=FakeSolicitudRepoVS(),
        trazabilidad_repo=FakeTrazabilidadRepoVS(dias_atras=10),
        borrador_repo=borrador_repo,
        seguimiento_repo=InMemSeguimientoRepo(),
        llm=FakeLLMAdapter(),
        timeout_proveedor_dias=7,
        proveedor_email="prov@test.com",
    )
    result = uc.execute()
    assert result["borradores_generados"] == 1
    assert borrador_repo._store[0].dias_sin_respuesta == 10
```

- [ ] **Step 2: Correr test para verificar que falla**

```bash
uv run pytest tests/application/test_verificar_estado_semanal_dias.py -v
```

Expected: FAIL — `AssertionError: assert 0 == 10` (dias_sin_respuesta is 0 because it's not set)

- [ ] **Step 3: Actualizar `VerificarEstadoSemanal._verificar_solicitud()`**

En `src/seguimiento/application/verificar_estado_semanal.py`, localizar la creación del `BorradorCorreo` (línea ~50) y agregar `dias_sin_respuesta`:

```python
        borrador = BorradorCorreo(
            solicitud_id=solicitud.id,
            destinatario_tipo=DestinatarioTipo.PROVEEDOR,
            destinatario_email=self._proveedor_email,
            asunto=email_data["asunto"],
            cuerpo=email_data["cuerpo"],
            dias_sin_respuesta=dias_sin_respuesta,  # ← NUEVO
        )
```

- [ ] **Step 4: Correr test para verificar que pasa**

```bash
uv run pytest tests/application/test_verificar_estado_semanal_dias.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/seguimiento/application/verificar_estado_semanal.py tests/application/test_verificar_estado_semanal_dias.py
git commit -m "fix: set dias_sin_respuesta on BorradorCorreo in VerificarEstadoSemanal"
```

---

## Task 5: Migración DB — agregar `dias_sin_respuesta` a `borradores_correo`

**Files:**
- Modify: `src/seguimiento/infrastructure/django_models.py`
- Modify: `src/seguimiento/infrastructure/repositories.py`
- Create: `src/seguimiento/infrastructure/migrations/0002_borrador_dias_sin_respuesta.py`

- [ ] **Step 1: Actualizar `django_models.py`**

Agregar el campo al final de `BorradorCorreoModel`:

```python
class BorradorCorreoModel(models.Model):
    solicitud_id = models.IntegerField()
    destinatario_tipo = models.CharField(max_length=50)
    destinatario_email = models.EmailField()
    asunto = models.CharField(max_length=300)
    cuerpo = models.TextField()
    estado = models.CharField(max_length=50, default="pendiente_aprobacion")
    aprobado_por = models.EmailField(blank=True, null=True)
    motivo_rechazo = models.TextField(blank=True, null=True)
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    dias_sin_respuesta = models.IntegerField(default=0)  # ← NUEVO
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "seguimiento"
        db_table = "borradores_correo"
```

- [ ] **Step 2: Crear la migración manualmente**

```python
# src/seguimiento/infrastructure/migrations/0002_borrador_dias_sin_respuesta.py
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("seguimiento", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="borradorcorreomodel",
            name="dias_sin_respuesta",
            field=models.IntegerField(default=0),
        ),
    ]
```

- [ ] **Step 3: Aplicar la migración**

```bash
docker compose up -d db
uv run python manage.py migrate
```

Expected: `Running migrations: Applying seguimiento.0002_borrador_dias_sin_respuesta... OK`

- [ ] **Step 4: Actualizar `repositories.py` para persistir y cargar el campo**

En `DjangoBorradorCorreoRepository.save()`, agregar `dias_sin_respuesta=b.dias_sin_respuesta` al dict de defaults:

```python
    def save(self, b: BorradorCorreo) -> None:
        pk = int(b.id) if b.id.isdigit() else None
        obj, created = BorradorCorreoModel.objects.update_or_create(
            id=pk,
            defaults=dict(
                solicitud_id=int(b.solicitud_id) if b.solicitud_id.isdigit() else 0,
                destinatario_tipo=b.destinatario_tipo.value,
                destinatario_email=b.destinatario_email,
                asunto=b.asunto,
                cuerpo=b.cuerpo,
                estado=b.estado.value,
                aprobado_por=b.aprobado_por,
                motivo_rechazo=b.motivo_rechazo,
                fecha_aprobacion=b.fecha_aprobacion,
                dias_sin_respuesta=b.dias_sin_respuesta,   # ← NUEVO
            ),
        )
        if created:
            b.id = str(obj.id)
```

En `_to_entity()`, agregar el campo:

```python
    def _to_entity(self, m: BorradorCorreoModel) -> BorradorCorreo:
        b = BorradorCorreo(
            id=str(m.id),
            solicitud_id=str(m.solicitud_id),
            destinatario_tipo=DestinatarioTipo(m.destinatario_tipo),
            destinatario_email=m.destinatario_email,
            asunto=m.asunto,
            cuerpo=m.cuerpo,
            estado=EstadoBorrador(m.estado),
            aprobado_por=m.aprobado_por,
            motivo_rechazo=m.motivo_rechazo,
            fecha_aprobacion=m.fecha_aprobacion,
            dias_sin_respuesta=m.dias_sin_respuesta,   # ← NUEVO
        )
        return b
```

- [ ] **Step 5: Correr tests de integración para verificar la migración**

```bash
uv run pytest tests/integration/ -v -k "borrador"
```

Expected: PASS (si no hay tests de integración para borradores, omitir)

- [ ] **Step 6: Commit**

```bash
git add src/seguimiento/infrastructure/django_models.py \
        src/seguimiento/infrastructure/repositories.py \
        src/seguimiento/infrastructure/migrations/0002_borrador_dias_sin_respuesta.py
git commit -m "feat: add dias_sin_respuesta column to borradores_correo table"
```

---

## Task 6: Actualizar fake adapters + prompt de Gemini

**Files:**
- Modify: `src/agente/infrastructure/email/fake_email_adapter.py`
- Modify: `src/agente/infrastructure/llm/fake_llm_adapter.py`
- Modify: `src/agente/infrastructure/llm/gemini_llm_adapter.py`

- [ ] **Step 1: Actualizar `fake_email_adapter.py` — agregar 2 nuevos correos al inbox**

Localizar `_FAKE_INBOX` y agregar al final de la lista:

```python
    CorreoEntrante(
        uid="fake-004",
        asunto="Confirmación recepción equipo - Kyocera KYO-TASKalfa-2021-001",
        cuerpo="Estimados, confirmamos recepción del equipo Kyocera TASKalfa serial KYO-TASKalfa-2021-001. Estimamos diagnóstico en 3 días hábiles.",
        remitente="soporte@kyocera.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    CorreoEntrante(
        uid="fake-005",
        asunto="Equipo reparado listo para retiro - Barco BAR-CS-2022-014",
        cuerpo="Estimados, el equipo Barco ClickShare serial BAR-CS-2022-014 ha sido reparado y está listo para retiro o devolución.",
        remitente="soporte@barco.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
```

- [ ] **Step 2: Actualizar `fake_llm_adapter.py` — agregar clasificación de `CONFIRMACION_DEVOLUCION`**

En el método `classify_email`, agregar ANTES del bloque `CONFIRMACION_DESPACHO`:

```python
        if any(w in texto for w in ["reparado", "listo para retiro", "devolvemos", "devolución", "devolucion", "repaired"]):
            return DecisionCorreo(
                tipo=TipoCorreo.CONFIRMACION_DEVOLUCION,
                confianza=0.95,
                equipo_serial=serial,
                nuevo_estado="devuelta",
                razonamiento="[FAKE] equipo reparado confirmado para retiro",
            )
```

También agregar el import del nuevo tipo (ya debería estar si se importa `TipoCorreo` completo).

- [ ] **Step 3: Actualizar `gemini_llm_adapter.py` — actualizar prompt de `classify_email`**

Localizar el string del prompt en `classify_email` y reemplazar la línea de tipos:

```python
# Cambiar de:
  "tipo": "acta_entrega" | "actualizacion_proveedor" | "consulta_cliente" | "confirmacion_despacho" | "otro",

# A:
  "tipo": "acta_entrega" | "actualizacion_proveedor" | "consulta_cliente" | "confirmacion_despacho" | "confirmacion_devolucion" | "otro",
```

Y agregar una línea de descripción en el prompt:

```python
prompt = f"""
Eres un agente de gestión de garantías para Datecsa S.A.
Clasifica el siguiente correo y responde SOLO con JSON válido (sin bloques markdown):
{{
  "tipo": "acta_entrega" | "actualizacion_proveedor" | "consulta_cliente" | "confirmacion_despacho" | "confirmacion_devolucion" | "otro",
  "confianza": float 0-1,
  "equipo_serial": "serial del equipo si se menciona, sino vacío",
  "nuevo_estado": "en_reparacion si confirmacion_despacho | devuelta si confirmacion_devolucion | sino vacío",
  "tiempo_estimado_dias": 0,
  "informacion_adicional": "datos relevantes extraídos del correo",
  "razonamiento": "por qué clasificaste así"
}}

Tipos:
- acta_entrega: el correo adjunta o describe una acta de entrega de un equipo con falla
- actualizacion_proveedor: el proveedor informa estado de la reparación en curso
- confirmacion_despacho: el proveedor confirma que recibió el equipo y lo tienen en reparación
- confirmacion_devolucion: el proveedor confirma que el equipo fue reparado y está listo para ser recogido/enviado de vuelta
- consulta_cliente: el cliente pregunta por el estado de su garantía
- otro: cualquier otro tipo de correo no relacionado con garantías

Asunto: {asunto}
Cuerpo: {cuerpo}
"""
```

- [ ] **Step 4: Correr los tests de aplicación para verificar que los fake adapters funcionan**

```bash
uv run pytest tests/application/ -v
```

Expected: todos PASS

- [ ] **Step 5: Commit**

```bash
git add src/agente/infrastructure/email/fake_email_adapter.py \
        src/agente/infrastructure/llm/fake_llm_adapter.py \
        src/agente/infrastructure/llm/gemini_llm_adapter.py
git commit -m "feat: update fake inbox with devolucion scenario, add CONFIRMACION_DEVOLUCION to LLM adapters"
```

---

## Task 7: Configuración, wiring y API

**Files:**
- Modify: `config/settings.py`
- Modify: `config/dependencies.py`
- Modify: `config/scheduler.py`
- Modify: `api/routers/agente.py`
- Modify: `api/routers/borradores.py`
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: Actualizar `config/settings.py` — agregar emails de contactos internos**

Después de `EMAIL_IMAP_FOLDER`, agregar:

```python
    # Internal contacts — set these in .env for production
    RESPONSABLE_GARANTIAS_EMAIL: str = "responsable@datecsa.com"
    BODEGA_EMAIL: str = "bodega@datecsa.com"
    DESPACHO_EMAIL: str = "despacho@datecsa.com"
    RECEPCION_EMAIL: str = "recepcion@datecsa.com"
```

- [ ] **Step 2: Actualizar `config/dependencies.py` — agregar `get_orquestar_acciones()`**

Agregar al final del archivo:

```python
def get_orquestar_acciones():
    from src.agente.application.orquestar_acciones import OrquestarAcciones
    return OrquestarAcciones(
        llm=get_llm_adapter(),
        borrador_repo=get_borrador_repo(),
        responsable_email=settings.RESPONSABLE_GARANTIAS_EMAIL,
        bodega_email=settings.BODEGA_EMAIL,
        despacho_email=settings.DESPACHO_EMAIL,
        recepcion_email=settings.RECEPCION_EMAIL,
    )
```

- [ ] **Step 3: Actualizar `config/scheduler.py` — pasar `OrquestarAcciones` al job**

En `_run_procesar_correos()`, agregar import y pasar al caso de uso:

```python
def _run_procesar_correos() -> None:
    from config.dependencies import (
        get_llm_adapter, get_email_reader, get_ocr_adapter,
        get_embedding_adapter, get_vector_store,
        get_solicitud_repo, get_garantia_repo, get_trazabilidad_repo,
        get_orquestar_acciones,
    )
    from src.agente.application.procesar_correo import ProcesarCorreo
    from src.solicitudes.application.crear_solicitud import CrearSolicitud

    solicitud_repo = get_solicitud_repo()
    caso_uso = ProcesarCorreo(
        llm=get_llm_adapter(),
        email_reader=get_email_reader(),
        ocr=get_ocr_adapter(),
        embedding=get_embedding_adapter(),
        vector_store=get_vector_store(),
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=get_trazabilidad_repo(),
        crear_solicitud=CrearSolicitud(
            solicitud_repo=solicitud_repo,
            garantia_repo=get_garantia_repo(),
        ),
        orquestar=get_orquestar_acciones(),
    )
    result = caso_uso.execute()
    if result["procesados"] > 0:
        import logging
        logging.getLogger(__name__).info(
            "procesar_correos: %d procesados", result["procesados"]
        )
```

- [ ] **Step 4: Actualizar `api/routers/agente.py` — endpoint `procesar_correos`**

Localizar el endpoint `@router.post("/procesar-correos")` y reemplazarlo:

```python
@router.post("/procesar-correos")
def procesar_correos(
    llm=Depends(get_llm_adapter),
    email_reader=Depends(get_email_reader),
    ocr=Depends(get_ocr_adapter),
    embedding=Depends(get_embedding_adapter),
    vector_store=Depends(get_vector_store),
    solicitud_repo=Depends(get_solicitud_repo),
    garantia_repo=Depends(get_garantia_repo),
    trazabilidad_repo=Depends(get_trazabilidad_repo),
):
    from src.agente.application.procesar_correo import ProcesarCorreo
    from src.solicitudes.application.crear_solicitud import CrearSolicitud
    from config.dependencies import get_orquestar_acciones

    caso_uso = ProcesarCorreo(
        llm=llm,
        email_reader=email_reader,
        ocr=ocr,
        embedding=embedding,
        vector_store=vector_store,
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=trazabilidad_repo,
        crear_solicitud=CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo),
        orquestar=get_orquestar_acciones(),
    )
    return caso_uso.execute()
```

- [ ] **Step 5: Actualizar `api/routers/borradores.py` — enriquecer `BorradorResponse`**

Reemplazar la clase `BorradorResponse` y todas sus instanciaciones:

```python
from datetime import datetime
from typing import Optional
from src.seguimiento.domain.entities import EstadoBorrador


class BorradorResponse(BaseModel):
    id: str
    solicitud_id: str
    destinatario_tipo: str
    destinatario_email: str
    asunto: str
    cuerpo: str
    estado: EstadoBorrador
    aprobado_por: Optional[str] = None
    fecha_aprobacion: Optional[datetime] = None
    dias_sin_respuesta: int = 0
```

Reemplazar todas las instanciaciones de `BorradorResponse(...)` en el archivo para incluir los nuevos campos:

```python
def _to_response(b) -> BorradorResponse:
    return BorradorResponse(
        id=b.id,
        solicitud_id=b.solicitud_id,
        destinatario_tipo=b.destinatario_tipo.value,
        destinatario_email=b.destinatario_email,
        asunto=b.asunto,
        cuerpo=b.cuerpo,
        estado=b.estado,
        aprobado_por=b.aprobado_por,
        fecha_aprobacion=b.fecha_aprobacion,
        dias_sin_respuesta=b.dias_sin_respuesta,
    )
```

Luego reemplazar cada `return BorradorResponse(id=b.id, ...)` con `return _to_response(b)` en todos los endpoints del archivo.

- [ ] **Step 6: Actualizar `frontend/src/types/index.ts` — enriquecer `BorradorCorreo`**

Localizar la interfaz `BorradorCorreo` y agregar los campos faltantes:

```typescript
export interface BorradorCorreo {
  id: string
  solicitud_id: string
  destinatario_tipo: 'proveedor' | 'cliente' | 'responsable' | 'bodega' | 'despacho' | 'recepcion'
  destinatario_email: string
  asunto: string
  cuerpo: string
  estado: 'pendiente_aprobacion' | 'aprobado' | 'rechazado' | 'enviado'
  aprobado_por?: string
  fecha_aprobacion?: string
  motivo_rechazo?: string
  dias_sin_respuesta: number
  created_at?: string
}
```

- [ ] **Step 7: Verificar TypeScript compila sin errores**

```bash
cd frontend && npx tsc --noEmit
```

Expected: sin errores

- [ ] **Step 8: Correr toda la suite de tests**

```bash
uv run pytest tests/unit/ tests/application/ -v
```

Expected: todos PASS

- [ ] **Step 9: Commit**

```bash
git add config/settings.py config/dependencies.py config/scheduler.py \
        api/routers/agente.py api/routers/borradores.py \
        frontend/src/types/index.ts
git commit -m "feat: wire OrquestarAcciones into scheduler, router, and update BorradorResponse schema"
```

---

## Verificación end-to-end

```bash
# 1. Backend arriba y DB migrada
docker compose up -d db
uv run uvicorn api.main:app --reload

# 2. Verificar que procesar-correos crea borradores para múltiples destinatarios
curl -s -X POST http://localhost:8000/agente/procesar-correos | python3 -m json.tool
# Esperado: procesados=5, cada detalle tiene borradores_generados y destinatarios

# 3. Verificar que los borradores aparecen en la lista con destinatario_tipo
curl -s http://localhost:8000/borradores/ | python3 -m json.tool
# Esperado: borradores con destinatario_tipo = "responsable" | "bodega" | "despacho" | etc.

# 4. Verificar que un borrador de verificacion_semanal tiene dias_sin_respuesta
curl -s -X POST http://localhost:8000/agente/verificar-semanal | python3 -m json.tool
curl -s http://localhost:8000/borradores/ | python3 -m json.tool
# Esperado: borrador con dias_sin_respuesta > 0

# 5. Abrir frontend http://localhost:5173 → "Correos para aprobar"
# Verificar: tarjetas muestran "Xd sin respuesta" para borradores de verificación semanal
# Verificar: el campo email muestra el correo correcto por tipo de destinatario

# 6. Test con Outlook real (si EMAIL_BACKEND=outlook está configurado)
# Enviar un correo a garantias_mock@outlook.com con asunto "Acta entrega - KYO-TASKalfa-2021-001"
# Esperar 5 minutos (polling interval) o triggear manualmente con el curl de arriba
# Verificar en la UI que se creó una solicitud + borrador para responsable
```

---

## Notas de implementación

- `OrquestarAcciones` usa `Optional[str]` defaults vacíos — si un email no está configurado en settings, no crea borrador para ese destinatario. Esto evita errores cuando la instalación no tiene todos los roles.
- `ProcesarCorreo.orquestar` es opcional (`None` por default) — el router de e2e tests que no pasan `OrquestarAcciones` seguirán funcionando sin cambios.
- La `InMemoryBorradorRepo` de los tests de Task 3 NO hereda de ninguna clase fake existente porque no la hay en tests/ — se define inline dentro del test para mantener los tests autocontenidos.
- El campo `dias_sin_respuesta` en `BorradorCorreo` es `int = 0` (no Optional) para simplificar el código del frontend — siempre tendrá un valor numérico.
- Los correos del fake inbox `fake-004` y `fake-005` usan seriales de equipos que ya existen en la DB (de los fixtures). Si la DB está vacía, `_manejar_actualizacion` retornará `"solicitud_activa_no_encontrada"` — esto es correcto, no es un error.
