# Datecsa Garantías POC — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Backend funcional end-to-end para gestión de garantías de equipos Datecsa (audiovisual e impresión) con agente IA que procesa PDFs y correos, trazabilidad completa y human-in-the-loop para aprobación de correos de seguimiento.

**Architecture:** Hexagonal por módulo — cada módulo (`equipos`, `solicitudes`, `trazabilidad`, `seguimiento`, `agente`, `notificaciones`) tiene capas `domain → application → infrastructure` independientes. Los módulos se comunican solo a través de casos de uso. Adapters intercambiables vía `settings.py`.

**Tech Stack:** Python, FastAPI, Django ORM (standalone), Pydantic + pydantic-settings, PostgreSQL + pgvector, Gemini text-embedding-004 (Matryoshka dim=768), FakeLLM/FakeEmbedding para tests, uv, Docker + Docker Compose, pytest, reportlab.

---

## Mapa de archivos

```
garantias_poc/
├── src/
│   ├── shared/domain/base.py                          # BaseEntity, ValueObject
│   ├── equipos/domain/entities.py                     # Equipo, Garantia, Proveedor, enums
│   ├── equipos/domain/ports.py                        # EquipoRepository, GarantiaRepository (ABC)
│   ├── equipos/application/registrar_equipo.py        # caso de uso
│   ├── equipos/application/verificar_garantia.py      # caso de uso
│   ├── equipos/infrastructure/django_models.py        # ORM models
│   ├── equipos/infrastructure/repositories.py         # implementaciones concretas
│   ├── solicitudes/domain/entities.py                 # SolicitudGarantia, ActaEntrega, estados
│   ├── solicitudes/domain/ports.py                    # SolicitudRepository (ABC)
│   ├── solicitudes/application/crear_solicitud.py
│   ├── solicitudes/application/actualizar_estado.py
│   ├── solicitudes/application/cerrar_garantia.py
│   ├── solicitudes/infrastructure/django_models.py
│   ├── solicitudes/infrastructure/repositories.py
│   ├── trazabilidad/domain/entities.py                # EventoTrazabilidad, UbicacionEquipo
│   ├── trazabilidad/domain/ports.py
│   ├── trazabilidad/application/registrar_movimiento.py
│   ├── trazabilidad/application/consultar_ubicacion.py
│   ├── trazabilidad/infrastructure/django_models.py
│   ├── trazabilidad/infrastructure/repositories.py
│   ├── seguimiento/domain/entities.py                 # BorradorCorreo, EventoSeguimiento
│   ├── seguimiento/domain/ports.py
│   ├── seguimiento/application/verificar_estado_semanal.py
│   ├── seguimiento/application/escalar_solicitud.py
│   ├── seguimiento/application/aprobar_borrador.py
│   ├── seguimiento/application/rechazar_borrador.py
│   ├── seguimiento/infrastructure/django_models.py
│   ├── seguimiento/infrastructure/repositories.py
│   ├── agente/domain/entities.py                      # DecisionAgente, Accion, Contexto
│   ├── agente/domain/ports.py                         # OCRPort, LLMPort, EmbeddingPort, EmailPort
│   ├── agente/application/procesar_documento.py
│   ├── agente/application/procesar_correo.py
│   ├── agente/application/buscar_similares.py
│   ├── agente/infrastructure/ocr/fake_ocr_adapter.py
│   ├── agente/infrastructure/ocr/gemini_ocr_adapter.py
│   ├── agente/infrastructure/llm/fake_llm_adapter.py
│   ├── agente/infrastructure/llm/gemini_llm_adapter.py
│   ├── agente/infrastructure/embeddings/fake_embedding_adapter.py
│   ├── agente/infrastructure/embeddings/gemini_embedding_adapter.py
│   ├── agente/infrastructure/email/fake_email_adapter.py
│   ├── agente/infrastructure/email/office365_adapter.py
│   ├── agente/infrastructure/chunking.py              # ChunkingService
│   ├── agente/infrastructure/vector_store.py          # pgvector queries
│   ├── notificaciones/domain/entities.py
│   ├── notificaciones/domain/ports.py
│   ├── notificaciones/application/enviar_notificacion.py
│   └── notificaciones/infrastructure/repositories.py
├── api/
│   ├── main.py
│   ├── routers/equipos.py
│   ├── routers/solicitudes.py
│   ├── routers/trazabilidad.py
│   ├── routers/borradores.py
│   ├── routers/agente.py
│   └── routers/notificaciones.py
├── config/
│   ├── settings.py
│   ├── database.py
│   └── dependencies.py
├── tests/
│   ├── conftest.py
│   ├── unit/test_equipos_domain.py
│   ├── unit/test_solicitudes_domain.py
│   ├── unit/test_trazabilidad_domain.py
│   ├── unit/test_seguimiento_domain.py
│   ├── application/test_registrar_equipo.py
│   ├── application/test_crear_solicitud.py
│   ├── application/test_verificar_estado_semanal.py
│   ├── application/test_aprobar_borrador.py
│   ├── integration/test_equipos_repository.py
│   ├── integration/test_solicitudes_repository.py
│   ├── integration/test_pgvector.py
│   └── e2e/test_flujo_garantia.py
├── fixtures/
│   ├── equipos.json
│   ├── garantias.json
│   ├── solicitudes.json
│   ├── proveedores.json
│   └── pdfs/
├── scripts/generate_fixtures.py
├── Makefile
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example
```

---

## Sprint 1 — Setup del proyecto

### Task 1: Inicializar proyecto con uv y estructura base

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `Makefile`
- Create: `docker-compose.yml`
- Create: `Dockerfile`

- [ ] **Step 1: Inicializar proyecto uv**

```bash
cd /Users/andrescadena/Documents/repos/datecsa_garantias
uv init --no-readme
uv add fastapi uvicorn[standard] django psycopg2-binary pgvector pydantic pydantic-settings python-dotenv reportlab
uv add --dev pytest pytest-asyncio httpx ruff mypy
```

- [ ] **Step 2: Crear estructura de directorios**

```bash
mkdir -p src/{shared/{domain,infrastructure},equipos/{domain,application,infrastructure},solicitudes/{domain,application,infrastructure},trazabilidad/{domain,application,infrastructure},seguimiento/{domain,application,infrastructure},agente/{domain,application,infrastructure/{ocr,llm,embeddings,email}},notificaciones/{domain,application,infrastructure}}
mkdir -p api/routers config tests/{unit,application,integration,e2e} fixtures/pdfs scripts
touch src/__init__.py
find src -type d -exec touch {}/__init__.py \;
find api -type d -exec touch {}/__init__.py \;
find config -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;
```

- [ ] **Step 3: Escribir docker-compose.yml**

```yaml
# docker-compose.yml
services:
  api:
    build: .
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app

  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: garantias
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d garantias"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

- [ ] **Step 4: Escribir Dockerfile**

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 5: Escribir .env.example**

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/garantias
LLM_PROVIDER=fake
GEMINI_API_KEY=
EMBEDDING_PROVIDER=fake
EMBEDDING_DIM=768
OCR_BACKEND=mock
EMAIL_BACKEND=mock
TIMEOUT_PROVEEDOR_DIAS=7
TIMEOUT_CLIENTE_DIAS=7
DEBUG=true
SECRET_KEY=dev-secret
DJANGO_SETTINGS_MODULE=config.django_settings
```

- [ ] **Step 6: Escribir Makefile**

```makefile
# Makefile
.PHONY: install dev docker-up docker-down docker-build \
        migrate fixtures test test-unit test-app test-integration test-e2e lint

install:
	cp -n .env.example .env || true
	uv sync

dev:
	docker compose up -d db
	uv run uvicorn api.main:app --reload

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v

migrate:
	uv run python -m django migrate --settings=config.django_settings

fixtures:
	uv run python scripts/generate_fixtures.py

test-unit:
	uv run pytest tests/unit/ -v

test-app:
	uv run pytest tests/application/ -v

test-integration:
	docker compose up -d db
	uv run pytest tests/integration/ -v

test-e2e:
	docker compose up -d db
	uv run pytest tests/e2e/ -v

test:
	uv run pytest tests/unit/ tests/application/ -v
	docker compose up -d db
	uv run pytest tests/integration/ tests/e2e/ -v

lint:
	uv run ruff check src/ api/ tests/
```

- [ ] **Step 7: Commit**

```bash
git init
git add .
git commit -m "chore: inicializar proyecto con uv, Docker y Makefile"
```

---

### Task 2: Configuración centralizada (settings + Django ORM standalone)

**Files:**
- Create: `config/settings.py`
- Create: `config/django_settings.py`
- Create: `config/database.py`
- Create: `config/dependencies.py`

- [ ] **Step 1: Escribir config/settings.py**

```python
# config/settings.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/garantias"

    LLM_PROVIDER: str = "fake"
    GEMINI_API_KEY: str = ""

    EMBEDDING_PROVIDER: str = "fake"
    EMBEDDING_DIM: int = 768

    OCR_BACKEND: str = "mock"
    EMAIL_BACKEND: str = "mock"
    EMAIL_HOST: str = ""

    TIMEOUT_PROVEEDOR_DIAS: int = 7
    TIMEOUT_CLIENTE_DIAS: int = 7

    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret"
    DJANGO_SETTINGS_MODULE: str = "config.django_settings"

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 2: Escribir config/django_settings.py**

```python
# config/django_settings.py
from config.settings import settings

SECRET_KEY = settings.SECRET_KEY
DEBUG = settings.DEBUG
INSTALLED_APPS = [
    "src.equipos.infrastructure",
    "src.solicitudes.infrastructure",
    "src.trazabilidad.infrastructure",
    "src.seguimiento.infrastructure",
    "src.notificaciones.infrastructure",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "garantias",
        "USER": "user",
        "PASSWORD": "pass",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

- [ ] **Step 3: Escribir config/database.py**

```python
# config/database.py
import django
from django.conf import settings as django_conf
import os


def setup_django() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django_settings")
    if not django_conf.configured:
        django.setup()
```

- [ ] **Step 4: Escribir config/dependencies.py (esqueleto — se llenará en sprints posteriores)**

```python
# config/dependencies.py
# Dependency injection para FastAPI — se completa en Sprint 4
```

- [ ] **Step 5: Commit**

```bash
git add config/
git commit -m "chore: configuración centralizada con pydantic-settings y Django ORM standalone"
```

---

## Sprint 2 — Dominio puro + unit tests

### Task 3: shared/domain — BaseEntity y ValueObject

**Files:**
- Create: `src/shared/domain/base.py`
- Create: `tests/unit/test_shared_domain.py`

- [ ] **Step 1: Escribir test que falla**

```python
# tests/unit/test_shared_domain.py
import uuid
from src.shared.domain.base import BaseEntity


def test_base_entity_tiene_id_unico():
    class ConcreteEntity(BaseEntity):
        pass

    e1 = ConcreteEntity()
    e2 = ConcreteEntity()
    assert e1.id != e2.id
    assert isinstance(e1.id, str)


def test_base_entity_acepta_id_existente():
    existing_id = str(uuid.uuid4())
    class ConcreteEntity(BaseEntity):
        pass
    e = ConcreteEntity(id=existing_id)
    assert e.id == existing_id
```

- [ ] **Step 2: Ejecutar test para verificar que falla**

```bash
uv run pytest tests/unit/test_shared_domain.py -v
```
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implementar src/shared/domain/base.py**

```python
# src/shared/domain/base.py
import uuid
from dataclasses import dataclass, field


@dataclass
class BaseEntity:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
```

- [ ] **Step 4: Verificar que los tests pasan**

```bash
uv run pytest tests/unit/test_shared_domain.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/shared/domain/base.py tests/unit/test_shared_domain.py
git commit -m "feat: BaseEntity con id autogenerado"
```

---

### Task 4: equipos/domain — Equipo, Garantia, Proveedor

**Files:**
- Create: `src/equipos/domain/entities.py`
- Create: `tests/unit/test_equipos_domain.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/unit/test_equipos_domain.py
import pytest
from datetime import date, timedelta
from src.equipos.domain.entities import (
    Equipo, Garantia, Proveedor, TipoEquipo, EstadoGarantia
)


def test_equipo_se_crea_con_datos_validos():
    equipo = Equipo(
        serial="KYO-TASKalfa-2021-001",
        nombre="Multifuncional Kyocera TASKalfa 2553ci",
        marca="Kyocera",
        modelo="TASKalfa 2553ci",
        tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION,
        ubicacion_fisica="Piso 3 - Área Administrativa",
    )
    assert equipo.serial == "KYO-TASKalfa-2021-001"
    assert equipo.tipo == TipoEquipo.MULTIFUNCIONAL_IMPRESION


def test_garantia_vigente_cuando_fecha_fin_es_futura():
    garantia = Garantia(
        equipo_id="equipo-1",
        proveedor_id="prov-1",
        fecha_inicio=date.today() - timedelta(days=30),
        fecha_fin=date.today() + timedelta(days=335),
        tipo_cobertura="Total",
    )
    assert garantia.esta_vigente()
    assert garantia.estado == EstadoGarantia.VIGENTE


def test_garantia_vencida_cuando_fecha_fin_es_pasada():
    garantia = Garantia(
        equipo_id="equipo-1",
        proveedor_id="prov-1",
        fecha_inicio=date.today() - timedelta(days=400),
        fecha_fin=date.today() - timedelta(days=35),
        tipo_cobertura="Total",
    )
    assert not garantia.esta_vigente()
    assert garantia.estado == EstadoGarantia.VENCIDA


def test_proveedor_tiene_tiempo_respuesta_por_defecto():
    proveedor = Proveedor(nombre="Kyocera Colombia", contacto_email="soporte@kyocera.co")
    assert proveedor.tiempo_respuesta_dias == 5
```

- [ ] **Step 2: Ejecutar tests para verificar que fallan**

```bash
uv run pytest tests/unit/test_equipos_domain.py -v
```
Expected: FAIL

- [ ] **Step 3: Implementar src/equipos/domain/entities.py**

```python
# src/equipos/domain/entities.py
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from src.shared.domain.base import BaseEntity


class TipoEquipo(str, Enum):
    MULTIFUNCIONAL_IMPRESION = "multifuncional_impresion"
    IMPRESORA_PRODUCCION = "impresora_produccion"
    COLABORACION_AUDIOVISUAL = "colaboracion_audiovisual"
    AUTOMATIZACION_SALA = "automatizacion_sala"
    AUDIO_CORPORATIVO = "audio_corporativo"
    SENALIZACION_DIGITAL = "senalizacion_digital"
    VIDEOCONFERENCIA = "videoconferencia"


class EstadoEquipo(str, Enum):
    ACTIVO = "activo"
    EN_GARANTIA = "en_garantia"
    EN_REPARACION = "en_reparacion"
    DADO_DE_BAJA = "dado_de_baja"


class EstadoGarantia(str, Enum):
    VIGENTE = "vigente"
    VENCIDA = "vencida"
    EN_PROCESO = "en_proceso"
    CERRADA = "cerrada"


@dataclass
class Equipo(BaseEntity):
    serial: str = ""
    nombre: str = ""
    marca: str = ""
    modelo: str = ""
    tipo: TipoEquipo = TipoEquipo.MULTIFUNCIONAL_IMPRESION
    ubicacion_fisica: str = ""
    estado: EstadoEquipo = EstadoEquipo.ACTIVO


@dataclass
class Proveedor(BaseEntity):
    nombre: str = ""
    contacto_email: str = ""
    telefono: str = ""
    tiempo_respuesta_dias: int = 5


@dataclass
class Garantia(BaseEntity):
    equipo_id: str = ""
    proveedor_id: str = ""
    fecha_inicio: date = field(default_factory=date.today)
    fecha_fin: date = field(default_factory=date.today)
    tipo_cobertura: str = ""
    numero_contrato: str = ""
    estado: EstadoGarantia = field(init=False)

    def __post_init__(self):
        self.estado = EstadoGarantia.VIGENTE if self.esta_vigente() else EstadoGarantia.VENCIDA

    def esta_vigente(self) -> bool:
        return self.fecha_fin >= date.today()
```

- [ ] **Step 4: Verificar que los tests pasan**

```bash
uv run pytest tests/unit/test_equipos_domain.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/equipos/domain/entities.py tests/unit/test_equipos_domain.py
git commit -m "feat: dominio Equipo, Garantia, Proveedor con reglas de negocio"
```

---

### Task 5: solicitudes/domain — SolicitudGarantia y transiciones de estado

**Files:**
- Create: `src/solicitudes/domain/entities.py`
- Create: `tests/unit/test_solicitudes_domain.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/unit/test_solicitudes_domain.py
import pytest
from datetime import date
from src.solicitudes.domain.entities import (
    SolicitudGarantia, ActaEntrega, EstadoSolicitud
)


def test_solicitud_inicia_en_estado_nueva():
    solicitud = SolicitudGarantia(
        equipo_id="equipo-1",
        garantia_id="garantia-1",
        reportado_por="Carlos Técnico",
        descripcion_falla="Error de fusor C3100, equipo no imprime",
    )
    assert solicitud.estado == EstadoSolicitud.NUEVA


def test_solicitud_transicion_valida_nueva_a_validada():
    solicitud = SolicitudGarantia(
        equipo_id="equipo-1",
        garantia_id="garantia-1",
        reportado_por="Carlos",
        descripcion_falla="Falla fusor",
    )
    solicitud.validar()
    assert solicitud.estado == EstadoSolicitud.VALIDADA


def test_solicitud_no_puede_cerrar_desde_nueva():
    solicitud = SolicitudGarantia(
        equipo_id="equipo-1",
        garantia_id="garantia-1",
        reportado_por="Carlos",
        descripcion_falla="Falla fusor",
    )
    with pytest.raises(ValueError, match="transición inválida"):
        solicitud.cerrar()


def test_flujo_completo_solicitud():
    s = SolicitudGarantia(equipo_id="e1", garantia_id="g1", reportado_por="Ana", descripcion_falla="Falla")
    s.validar()
    s.despachar()
    s.iniciar_reparacion()
    s.devolver()
    s.cerrar()
    assert s.estado == EstadoSolicitud.CERRADA
```

- [ ] **Step 2: Ejecutar tests para verificar que fallan**

```bash
uv run pytest tests/unit/test_solicitudes_domain.py -v
```
Expected: FAIL

- [ ] **Step 3: Implementar src/solicitudes/domain/entities.py**

```python
# src/solicitudes/domain/entities.py
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from src.shared.domain.base import BaseEntity


class EstadoSolicitud(str, Enum):
    NUEVA = "nueva"
    VALIDADA = "validada"
    DESPACHADA = "despachada"
    EN_REPARACION = "en_reparacion"
    DEVUELTA = "devuelta"
    CERRADA = "cerrada"


_TRANSICIONES_VALIDAS: dict[EstadoSolicitud, list[EstadoSolicitud]] = {
    EstadoSolicitud.NUEVA: [EstadoSolicitud.VALIDADA],
    EstadoSolicitud.VALIDADA: [EstadoSolicitud.DESPACHADA],
    EstadoSolicitud.DESPACHADA: [EstadoSolicitud.EN_REPARACION],
    EstadoSolicitud.EN_REPARACION: [EstadoSolicitud.DEVUELTA],
    EstadoSolicitud.DEVUELTA: [EstadoSolicitud.CERRADA],
    EstadoSolicitud.CERRADA: [],
}


@dataclass
class SolicitudGarantia(BaseEntity):
    equipo_id: str = ""
    garantia_id: str = ""
    reportado_por: str = ""
    descripcion_falla: str = ""
    fecha_reporte: date = field(default_factory=date.today)
    estado: EstadoSolicitud = EstadoSolicitud.NUEVA

    def _transicionar(self, nuevo_estado: EstadoSolicitud) -> None:
        if nuevo_estado not in _TRANSICIONES_VALIDAS[self.estado]:
            raise ValueError(
                f"transición inválida: {self.estado} → {nuevo_estado}"
            )
        self.estado = nuevo_estado

    def validar(self) -> None:
        self._transicionar(EstadoSolicitud.VALIDADA)

    def despachar(self) -> None:
        self._transicionar(EstadoSolicitud.DESPACHADA)

    def iniciar_reparacion(self) -> None:
        self._transicionar(EstadoSolicitud.EN_REPARACION)

    def devolver(self) -> None:
        self._transicionar(EstadoSolicitud.DEVUELTA)

    def cerrar(self) -> None:
        self._transicionar(EstadoSolicitud.CERRADA)


@dataclass
class ActaEntrega(BaseEntity):
    solicitud_id: str = ""
    tecnico_responsable: str = ""
    fecha_entrega: date = field(default_factory=date.today)
    observaciones: str = ""
    imagen_acta_path: str = ""
```

- [ ] **Step 4: Verificar que los tests pasan**

```bash
uv run pytest tests/unit/test_solicitudes_domain.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/solicitudes/domain/entities.py tests/unit/test_solicitudes_domain.py
git commit -m "feat: dominio SolicitudGarantia con máquina de estados validada"
```

---

### Task 6: trazabilidad/domain + seguimiento/domain

**Files:**
- Create: `src/trazabilidad/domain/entities.py`
- Create: `src/seguimiento/domain/entities.py`
- Create: `tests/unit/test_trazabilidad_domain.py`
- Create: `tests/unit/test_seguimiento_domain.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/unit/test_trazabilidad_domain.py
from src.trazabilidad.domain.entities import EventoTrazabilidad, MetodoRegistro


def test_evento_trazabilidad_registra_movimiento():
    evento = EventoTrazabilidad(
        equipo_id="equipo-1",
        solicitud_id="sol-1",
        ubicacion_anterior="Piso 3 - Área Administrativa",
        ubicacion_nueva="Almacén Servicio Técnico",
        responsable="Carlos Técnico",
        metodo_registro=MetodoRegistro.MANUAL,
    )
    assert evento.ubicacion_nueva == "Almacén Servicio Técnico"
    assert evento.metodo_registro == MetodoRegistro.MANUAL
```

```python
# tests/unit/test_seguimiento_domain.py
import pytest
from src.seguimiento.domain.entities import BorradorCorreo, EstadoBorrador, DestinatarioTipo


def test_borrador_inicia_pendiente_aprobacion():
    borrador = BorradorCorreo(
        solicitud_id="sol-1",
        destinatario_tipo=DestinatarioTipo.PROVEEDOR,
        destinatario_email="soporte@kyocera.co",
        asunto="Seguimiento garantía KYO-TASKalfa-2021-001",
        cuerpo="Estimados, solicitamos amablemente...",
    )
    assert borrador.estado == EstadoBorrador.PENDIENTE_APROBACION


def test_borrador_aprobado_registra_aprobador():
    borrador = BorradorCorreo(
        solicitud_id="sol-1",
        destinatario_tipo=DestinatarioTipo.PROVEEDOR,
        destinatario_email="soporte@kyocera.co",
        asunto="Seguimiento",
        cuerpo="...",
    )
    borrador.aprobar(aprobado_por="juan@datecsa.com")
    assert borrador.estado == EstadoBorrador.APROBADO
    assert borrador.aprobado_por == "juan@datecsa.com"


def test_borrador_no_se_puede_aprobar_si_ya_fue_enviado():
    borrador = BorradorCorreo(
        solicitud_id="sol-1",
        destinatario_tipo=DestinatarioTipo.PROVEEDOR,
        destinatario_email="soporte@kyocera.co",
        asunto="Seguimiento",
        cuerpo="...",
    )
    borrador.aprobar(aprobado_por="juan@datecsa.com")
    borrador.marcar_enviado()
    with pytest.raises(ValueError, match="ya fue enviado"):
        borrador.aprobar(aprobado_por="otro@datecsa.com")


def test_borrador_rechazado_no_puede_enviarse():
    borrador = BorradorCorreo(
        solicitud_id="sol-1",
        destinatario_tipo=DestinatarioTipo.CLIENTE,
        destinatario_email="cliente@empresa.co",
        asunto="Seguimiento",
        cuerpo="...",
    )
    borrador.rechazar(motivo="Tono incorrecto")
    with pytest.raises(ValueError, match="no está aprobado"):
        borrador.marcar_enviado()
```

- [ ] **Step 2: Ejecutar tests para verificar que fallan**

```bash
uv run pytest tests/unit/test_trazabilidad_domain.py tests/unit/test_seguimiento_domain.py -v
```
Expected: FAIL

- [ ] **Step 3: Implementar src/trazabilidad/domain/entities.py**

```python
# src/trazabilidad/domain/entities.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from src.shared.domain.base import BaseEntity


class MetodoRegistro(str, Enum):
    MANUAL = "manual"
    AGENTE_OCR = "agente_ocr"
    AGENTE_EMAIL = "agente_email"


@dataclass
class EventoTrazabilidad(BaseEntity):
    equipo_id: str = ""
    solicitud_id: str = ""
    ubicacion_anterior: str = ""
    ubicacion_nueva: str = ""
    responsable: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metodo_registro: MetodoRegistro = MetodoRegistro.MANUAL
```

- [ ] **Step 4: Implementar src/seguimiento/domain/entities.py**

```python
# src/seguimiento/domain/entities.py
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional
from src.shared.domain.base import BaseEntity


class EstadoBorrador(str, Enum):
    PENDIENTE_APROBACION = "pendiente_aprobacion"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    ENVIADO = "enviado"


class DestinatarioTipo(str, Enum):
    PROVEEDOR = "proveedor"
    CLIENTE = "cliente"


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

    def aprobar(self, aprobado_por: str) -> None:
        if self.estado == EstadoBorrador.ENVIADO:
            raise ValueError("ya fue enviado")
        if self.estado == EstadoBorrador.RECHAZADO:
            raise ValueError("fue rechazado, no se puede aprobar")
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


@dataclass
class EventoSeguimiento(BaseEntity):
    solicitud_id: str = ""
    tipo_evento: str = ""
    descripcion: str = ""
    fecha: date = field(default_factory=date.today)
    dias_sin_respuesta: int = 0
```

- [ ] **Step 5: Verificar que los tests pasan**

```bash
uv run pytest tests/unit/test_trazabilidad_domain.py tests/unit/test_seguimiento_domain.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/trazabilidad/ src/seguimiento/ tests/unit/test_trazabilidad_domain.py tests/unit/test_seguimiento_domain.py
git commit -m "feat: dominio trazabilidad y seguimiento con BorradorCorreo validado"
```

---

## Sprint 3 — Puertos y repositorios en memoria

### Task 7: Puertos (interfaces) de repositorios

**Files:**
- Create: `src/equipos/domain/ports.py`
- Create: `src/solicitudes/domain/ports.py`
- Create: `src/trazabilidad/domain/ports.py`
- Create: `src/seguimiento/domain/ports.py`

- [ ] **Step 1: Crear puertos para cada módulo**

```python
# src/equipos/domain/ports.py
from abc import ABC, abstractmethod
from typing import Optional
from src.equipos.domain.entities import Equipo, Garantia, Proveedor


class EquipoRepository(ABC):
    @abstractmethod
    def save(self, equipo: Equipo) -> None: ...

    @abstractmethod
    def find_by_serial(self, serial: str) -> Optional[Equipo]: ...

    @abstractmethod
    def find_all(self) -> list[Equipo]: ...


class GarantiaRepository(ABC):
    @abstractmethod
    def save(self, garantia: Garantia) -> None: ...

    @abstractmethod
    def find_vigente_by_equipo(self, equipo_id: str) -> Optional[Garantia]: ...


class ProveedorRepository(ABC):
    @abstractmethod
    def save(self, proveedor: Proveedor) -> None: ...

    @abstractmethod
    def find_by_id(self, proveedor_id: str) -> Optional[Proveedor]: ...
```

```python
# src/solicitudes/domain/ports.py
from abc import ABC, abstractmethod
from typing import Optional
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud


class SolicitudRepository(ABC):
    @abstractmethod
    def save(self, solicitud: SolicitudGarantia) -> None: ...

    @abstractmethod
    def find_by_id(self, solicitud_id: str) -> Optional[SolicitudGarantia]: ...

    @abstractmethod
    def find_by_estado(self, estado: EstadoSolicitud) -> list[SolicitudGarantia]: ...

    @abstractmethod
    def find_all(self) -> list[SolicitudGarantia]: ...
```

```python
# src/trazabilidad/domain/ports.py
from abc import ABC, abstractmethod
from src.trazabilidad.domain.entities import EventoTrazabilidad


class TrazabilidadRepository(ABC):
    @abstractmethod
    def save(self, evento: EventoTrazabilidad) -> None: ...

    @abstractmethod
    def find_by_equipo(self, equipo_id: str) -> list[EventoTrazabilidad]: ...

    @abstractmethod
    def find_by_solicitud(self, solicitud_id: str) -> list[EventoTrazabilidad]: ...

    @abstractmethod
    def find_ultimo_evento(self, solicitud_id: str) -> EventoTrazabilidad | None: ...
```

```python
# src/seguimiento/domain/ports.py
from abc import ABC, abstractmethod
from typing import Optional
from src.seguimiento.domain.entities import BorradorCorreo, EventoSeguimiento, EstadoBorrador


class BorradorCorreoRepository(ABC):
    @abstractmethod
    def save(self, borrador: BorradorCorreo) -> None: ...

    @abstractmethod
    def find_by_id(self, borrador_id: str) -> Optional[BorradorCorreo]: ...

    @abstractmethod
    def find_pendientes(self) -> list[BorradorCorreo]: ...

    @abstractmethod
    def find_by_solicitud_y_estado(
        self, solicitud_id: str, estado: EstadoBorrador
    ) -> Optional[BorradorCorreo]: ...


class EventoSeguimientoRepository(ABC):
    @abstractmethod
    def save(self, evento: EventoSeguimiento) -> None: ...

    @abstractmethod
    def find_by_solicitud(self, solicitud_id: str) -> list[EventoSeguimiento]: ...
```

- [ ] **Step 2: Commit**

```bash
git add src/equipos/domain/ports.py src/solicitudes/domain/ports.py src/trazabilidad/domain/ports.py src/seguimiento/domain/ports.py
git commit -m "feat: puertos (interfaces) de repositorios para todos los módulos"
```

---

### Task 8: FakeRepositories + casos de uso + application tests

**Files:**
- Create: `tests/application/fakes.py`
- Create: `src/equipos/application/registrar_equipo.py`
- Create: `src/solicitudes/application/crear_solicitud.py`
- Create: `src/seguimiento/application/verificar_estado_semanal.py`
- Create: `src/seguimiento/application/escalar_solicitud.py`
- Create: `src/seguimiento/application/aprobar_borrador.py`
- Create: `src/seguimiento/application/rechazar_borrador.py`
- Create: `tests/application/test_registrar_equipo.py`
- Create: `tests/application/test_crear_solicitud.py`
- Create: `tests/application/test_verificar_estado_semanal.py`
- Create: `tests/application/test_aprobar_borrador.py`

- [ ] **Step 1: Crear FakeRepositories compartidos**

```python
# tests/application/fakes.py
from typing import Optional
from src.equipos.domain.entities import Equipo, Garantia, Proveedor
from src.equipos.domain.ports import EquipoRepository, GarantiaRepository, ProveedorRepository
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.solicitudes.domain.ports import SolicitudRepository
from src.trazabilidad.domain.entities import EventoTrazabilidad
from src.trazabilidad.domain.ports import TrazabilidadRepository
from src.seguimiento.domain.entities import BorradorCorreo, EventoSeguimiento, EstadoBorrador
from src.seguimiento.domain.ports import BorradorCorreoRepository, EventoSeguimientoRepository


class FakeEquipoRepository(EquipoRepository):
    def __init__(self):
        self._store: dict[str, Equipo] = {}

    def save(self, equipo: Equipo) -> None:
        self._store[equipo.serial] = equipo

    def find_by_serial(self, serial: str) -> Optional[Equipo]:
        return self._store.get(serial)

    def find_all(self) -> list[Equipo]:
        return list(self._store.values())


class FakeGarantiaRepository(GarantiaRepository):
    def __init__(self):
        self._store: dict[str, Garantia] = {}

    def save(self, garantia: Garantia) -> None:
        self._store[garantia.id] = garantia

    def find_vigente_by_equipo(self, equipo_id: str) -> Optional[Garantia]:
        return next(
            (g for g in self._store.values() if g.equipo_id == equipo_id and g.esta_vigente()),
            None,
        )


class FakeSolicitudRepository(SolicitudRepository):
    def __init__(self):
        self._store: dict[str, SolicitudGarantia] = {}

    def save(self, solicitud: SolicitudGarantia) -> None:
        self._store[solicitud.id] = solicitud

    def find_by_id(self, solicitud_id: str) -> Optional[SolicitudGarantia]:
        return self._store.get(solicitud_id)

    def find_by_estado(self, estado: EstadoSolicitud) -> list[SolicitudGarantia]:
        return [s for s in self._store.values() if s.estado == estado]

    def find_all(self) -> list[SolicitudGarantia]:
        return list(self._store.values())


class FakeTrazabilidadRepository(TrazabilidadRepository):
    def __init__(self):
        self._store: list[EventoTrazabilidad] = []

    def save(self, evento: EventoTrazabilidad) -> None:
        self._store.append(evento)

    def find_by_equipo(self, equipo_id: str) -> list[EventoTrazabilidad]:
        return [e for e in self._store if e.equipo_id == equipo_id]

    def find_by_solicitud(self, solicitud_id: str) -> list[EventoTrazabilidad]:
        return [e for e in self._store if e.solicitud_id == solicitud_id]

    def find_ultimo_evento(self, solicitud_id: str) -> Optional[EventoTrazabilidad]:
        eventos = self.find_by_solicitud(solicitud_id)
        return max(eventos, key=lambda e: e.timestamp, default=None)


class FakeBorradorCorreoRepository(BorradorCorreoRepository):
    def __init__(self):
        self._store: dict[str, BorradorCorreo] = {}

    def save(self, borrador: BorradorCorreo) -> None:
        self._store[borrador.id] = borrador

    def find_by_id(self, borrador_id: str) -> Optional[BorradorCorreo]:
        return self._store.get(borrador_id)

    def find_pendientes(self) -> list[BorradorCorreo]:
        return [b for b in self._store.values() if b.estado == EstadoBorrador.PENDIENTE_APROBACION]

    def find_by_solicitud_y_estado(
        self, solicitud_id: str, estado: EstadoBorrador
    ) -> Optional[BorradorCorreo]:
        return next(
            (b for b in self._store.values() if b.solicitud_id == solicitud_id and b.estado == estado),
            None,
        )


class FakeEventoSeguimientoRepository(EventoSeguimientoRepository):
    def __init__(self):
        self._store: list[EventoSeguimiento] = []

    def save(self, evento: EventoSeguimiento) -> None:
        self._store.append(evento)

    def find_by_solicitud(self, solicitud_id: str) -> list[EventoSeguimiento]:
        return [e for e in self._store if e.solicitud_id == solicitud_id]
```

- [ ] **Step 2: Escribir tests de application que fallan**

```python
# tests/application/test_registrar_equipo.py
from datetime import date, timedelta
from src.equipos.domain.entities import TipoEquipo
from src.equipos.application.registrar_equipo import RegistrarEquipo
from tests.application.fakes import FakeEquipoRepository


def test_registrar_equipo_lo_persiste():
    repo = FakeEquipoRepository()
    caso_uso = RegistrarEquipo(equipo_repo=repo)

    caso_uso.execute(
        serial="KYO-TASKalfa-2021-001",
        nombre="Multifuncional Kyocera TASKalfa 2553ci",
        marca="Kyocera",
        modelo="TASKalfa 2553ci",
        tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION,
        ubicacion_fisica="Piso 3 - Área Administrativa",
    )

    equipo = repo.find_by_serial("KYO-TASKalfa-2021-001")
    assert equipo is not None
    assert equipo.marca == "Kyocera"


def test_registrar_equipo_duplicado_lanza_error():
    repo = FakeEquipoRepository()
    caso_uso = RegistrarEquipo(equipo_repo=repo)
    caso_uso.execute(
        serial="KYO-001", nombre="Kyocera", marca="Kyocera",
        modelo="TASKalfa", tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION, ubicacion_fisica="Piso 1"
    )
    with pytest.raises(ValueError, match="serial ya existe"):
        caso_uso.execute(
            serial="KYO-001", nombre="Kyocera2", marca="Kyocera",
            modelo="TASKalfa", tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION, ubicacion_fisica="Piso 2"
        )
```

```python
# tests/application/test_aprobar_borrador.py
import pytest
from src.seguimiento.application.aprobar_borrador import AprobarBorrador
from src.seguimiento.application.rechazar_borrador import RechazarBorrador
from src.seguimiento.domain.entities import BorradorCorreo, DestinatarioTipo, EstadoBorrador
from tests.application.fakes import FakeBorradorCorreoRepository, FakeEquipoRepository


class FakeEmailAdapter:
    def __init__(self):
        self.sent: list[dict] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})


def _crear_borrador(repo):
    borrador = BorradorCorreo(
        solicitud_id="sol-1",
        destinatario_tipo=DestinatarioTipo.PROVEEDOR,
        destinatario_email="soporte@kyocera.co",
        asunto="Seguimiento garantía Kyocera",
        cuerpo="Estimados, solicitamos amablemente una actualización...",
    )
    repo.save(borrador)
    return borrador


def test_aprobar_borrador_lo_envía():
    repo = FakeBorradorCorreoRepository()
    email_adapter = FakeEmailAdapter()
    borrador = _crear_borrador(repo)

    caso_uso = AprobarBorrador(borrador_repo=repo, email_adapter=email_adapter)
    caso_uso.execute(borrador_id=borrador.id, aprobado_por="juan@datecsa.com")

    borrador_actualizado = repo.find_by_id(borrador.id)
    assert borrador_actualizado.estado == EstadoBorrador.ENVIADO
    assert borrador_actualizado.aprobado_por == "juan@datecsa.com"
    assert len(email_adapter.sent) == 1
    assert email_adapter.sent[0]["to"] == "soporte@kyocera.co"


def test_rechazar_borrador_no_envia_correo():
    repo = FakeBorradorCorreoRepository()
    email_adapter = FakeEmailAdapter()
    borrador = _crear_borrador(repo)

    caso_uso = RechazarBorrador(borrador_repo=repo)
    caso_uso.execute(borrador_id=borrador.id, motivo="El tono no es adecuado")

    borrador_actualizado = repo.find_by_id(borrador.id)
    assert borrador_actualizado.estado == EstadoBorrador.RECHAZADO
    assert len(email_adapter.sent) == 0
```

- [ ] **Step 3: Ejecutar tests para verificar que fallan**

```bash
uv run pytest tests/application/ -v
```
Expected: FAIL

- [ ] **Step 4: Implementar casos de uso**

```python
# src/equipos/application/registrar_equipo.py
from src.equipos.domain.entities import Equipo, TipoEquipo
from src.equipos.domain.ports import EquipoRepository


class RegistrarEquipo:
    def __init__(self, equipo_repo: EquipoRepository):
        self._repo = equipo_repo

    def execute(
        self,
        serial: str,
        nombre: str,
        marca: str,
        modelo: str,
        tipo: TipoEquipo,
        ubicacion_fisica: str,
    ) -> Equipo:
        if self._repo.find_by_serial(serial) is not None:
            raise ValueError(f"serial ya existe: {serial}")
        equipo = Equipo(
            serial=serial,
            nombre=nombre,
            marca=marca,
            modelo=modelo,
            tipo=tipo,
            ubicacion_fisica=ubicacion_fisica,
        )
        self._repo.save(equipo)
        return equipo
```

```python
# src/solicitudes/application/crear_solicitud.py
from src.solicitudes.domain.entities import SolicitudGarantia
from src.solicitudes.domain.ports import SolicitudRepository
from src.equipos.domain.ports import GarantiaRepository


class CrearSolicitud:
    def __init__(self, solicitud_repo: SolicitudRepository, garantia_repo: GarantiaRepository):
        self._solicitud_repo = solicitud_repo
        self._garantia_repo = garantia_repo

    def execute(
        self, equipo_id: str, reportado_por: str, descripcion_falla: str
    ) -> SolicitudGarantia:
        garantia = self._garantia_repo.find_vigente_by_equipo(equipo_id)
        if garantia is None:
            raise ValueError(f"equipo {equipo_id} no tiene garantía vigente")
        solicitud = SolicitudGarantia(
            equipo_id=equipo_id,
            garantia_id=garantia.id,
            reportado_por=reportado_por,
            descripcion_falla=descripcion_falla,
        )
        self._solicitud_repo.save(solicitud)
        return solicitud
```

```python
# src/seguimiento/application/aprobar_borrador.py
from src.seguimiento.domain.ports import BorradorCorreoRepository
from src.agente.domain.ports import EmailPort


class AprobarBorrador:
    def __init__(self, borrador_repo: BorradorCorreoRepository, email_adapter: EmailPort):
        self._repo = borrador_repo
        self._email = email_adapter

    def execute(self, borrador_id: str, aprobado_por: str) -> None:
        borrador = self._repo.find_by_id(borrador_id)
        if borrador is None:
            raise ValueError(f"borrador {borrador_id} no encontrado")
        borrador.aprobar(aprobado_por=aprobado_por)
        self._email.send(
            to=borrador.destinatario_email,
            subject=borrador.asunto,
            body=borrador.cuerpo,
        )
        borrador.marcar_enviado()
        self._repo.save(borrador)
```

```python
# src/seguimiento/application/rechazar_borrador.py
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
```

- [ ] **Step 5: Escribir EmailPort en agente/domain/ports.py**

```python
# src/agente/domain/ports.py
from abc import ABC, abstractmethod


class EmailPort(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> None: ...
```

- [ ] **Step 6: Verificar que los tests pasan**

```bash
uv run pytest tests/application/ -v
```
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/ tests/application/
git commit -m "feat: casos de uso con FakeRepositories y tests de aplicación"
```

---

## Sprint 4 — Django ORM + FastAPI

### Task 9: Django ORM models + repositorios concretos

**Files:**
- Create: `src/equipos/infrastructure/apps.py`
- Create: `src/equipos/infrastructure/django_models.py`
- Create: `src/equipos/infrastructure/repositories.py`
- Create: `src/solicitudes/infrastructure/apps.py`
- Create: `src/solicitudes/infrastructure/django_models.py`
- Create: `src/solicitudes/infrastructure/repositories.py`

- [ ] **Step 1: Equipos — Django models**

```python
# src/equipos/infrastructure/apps.py
from django.apps import AppConfig

class EquiposConfig(AppConfig):
    name = "src.equipos.infrastructure"
    label = "equipos"
```

```python
# src/equipos/infrastructure/django_models.py
from django.db import models


class EquipoModel(models.Model):
    serial = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    ubicacion_fisica = models.CharField(max_length=200)
    estado = models.CharField(max_length=50, default="activo")

    class Meta:
        app_label = "equipos"
        db_table = "equipos"


class ProveedorModel(models.Model):
    nombre = models.CharField(max_length=200)
    contacto_email = models.EmailField()
    telefono = models.CharField(max_length=50, blank=True)
    tiempo_respuesta_dias = models.IntegerField(default=5)

    class Meta:
        app_label = "equipos"
        db_table = "proveedores"


class GarantiaModel(models.Model):
    equipo = models.ForeignKey(EquipoModel, on_delete=models.CASCADE, related_name="garantias", to_field="serial")
    proveedor = models.ForeignKey(ProveedorModel, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo_cobertura = models.CharField(max_length=200)
    numero_contrato = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=50)

    class Meta:
        app_label = "equipos"
        db_table = "garantias"
```

- [ ] **Step 2: Equipos — Repositorio concreto**

```python
# src/equipos/infrastructure/repositories.py
from typing import Optional
from src.equipos.domain.entities import Equipo, Garantia, Proveedor, TipoEquipo, EstadoEquipo, EstadoGarantia
from src.equipos.domain.ports import EquipoRepository, GarantiaRepository
from src.equipos.infrastructure.django_models import EquipoModel, GarantiaModel
from datetime import date


class DjangoEquipoRepository(EquipoRepository):
    def save(self, equipo: Equipo) -> None:
        EquipoModel.objects.update_or_create(
            serial=equipo.serial,
            defaults=dict(
                nombre=equipo.nombre, marca=equipo.marca, modelo=equipo.modelo,
                tipo=equipo.tipo.value, ubicacion_fisica=equipo.ubicacion_fisica,
                estado=equipo.estado.value,
            ),
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
        return Equipo(
            serial=m.serial, nombre=m.nombre, marca=m.marca, modelo=m.modelo,
            tipo=TipoEquipo(m.tipo), ubicacion_fisica=m.ubicacion_fisica,
            estado=EstadoEquipo(m.estado),
        )


class DjangoGarantiaRepository(GarantiaRepository):
    def save(self, garantia: Garantia) -> None:
        equipo_model = EquipoModel.objects.get(serial=garantia.equipo_id)
        GarantiaModel.objects.update_or_create(
            id=garantia.id if garantia.id else None,
            defaults=dict(
                equipo=equipo_model, proveedor_id=garantia.proveedor_id,
                fecha_inicio=garantia.fecha_inicio, fecha_fin=garantia.fecha_fin,
                tipo_cobertura=garantia.tipo_cobertura, estado=garantia.estado.value,
            ),
        )

    def find_vigente_by_equipo(self, equipo_id: str) -> Optional[Garantia]:
        try:
            m = GarantiaModel.objects.filter(
                equipo__serial=equipo_id, fecha_fin__gte=date.today()
            ).latest("fecha_fin")
            return Garantia(
                equipo_id=equipo_id, proveedor_id=str(m.proveedor_id),
                fecha_inicio=m.fecha_inicio, fecha_fin=m.fecha_fin,
                tipo_cobertura=m.tipo_cobertura,
            )
        except GarantiaModel.DoesNotExist:
            return None
```

- [ ] **Step 3: Solicitudes — Django models y repositorio (patrón idéntico)**

```python
# src/solicitudes/infrastructure/apps.py
from django.apps import AppConfig

class SolicitudesConfig(AppConfig):
    name = "src.solicitudes.infrastructure"
    label = "solicitudes"
```

```python
# src/solicitudes/infrastructure/django_models.py
from django.db import models


class SolicitudGarantiaModel(models.Model):
    equipo_serial = models.CharField(max_length=100)
    garantia_id = models.CharField(max_length=100)
    reportado_por = models.CharField(max_length=200)
    descripcion_falla = models.TextField()
    fecha_reporte = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=50, default="nueva")

    class Meta:
        app_label = "solicitudes"
        db_table = "solicitudes_garantia"
```

```python
# src/solicitudes/infrastructure/repositories.py
from typing import Optional
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.solicitudes.domain.ports import SolicitudRepository
from src.solicitudes.infrastructure.django_models import SolicitudGarantiaModel


class DjangoSolicitudRepository(SolicitudRepository):
    def save(self, solicitud: SolicitudGarantia) -> None:
        SolicitudGarantiaModel.objects.update_or_create(
            id=solicitud.id,
            defaults=dict(
                equipo_serial=solicitud.equipo_id,
                garantia_id=solicitud.garantia_id,
                reportado_por=solicitud.reportado_por,
                descripcion_falla=solicitud.descripcion_falla,
                estado=solicitud.estado.value,
            ),
        )

    def find_by_id(self, solicitud_id: str) -> Optional[SolicitudGarantia]:
        try:
            m = SolicitudGarantiaModel.objects.get(id=solicitud_id)
            return self._to_entity(m)
        except SolicitudGarantiaModel.DoesNotExist:
            return None

    def find_by_estado(self, estado: EstadoSolicitud) -> list[SolicitudGarantia]:
        return [self._to_entity(m) for m in SolicitudGarantiaModel.objects.filter(estado=estado.value)]

    def find_all(self) -> list[SolicitudGarantia]:
        return [self._to_entity(m) for m in SolicitudGarantiaModel.objects.all()]

    def _to_entity(self, m: SolicitudGarantiaModel) -> SolicitudGarantia:
        return SolicitudGarantia(
            id=str(m.id), equipo_id=m.equipo_serial, garantia_id=m.garantia_id,
            reportado_por=m.reportado_por, descripcion_falla=m.descripcion_falla,
            fecha_reporte=m.fecha_reporte, estado=EstadoSolicitud(m.estado),
        )
```

- [ ] **Step 4: Correr migraciones**

```bash
make migrate
```
Expected: tablas creadas en PostgreSQL

- [ ] **Step 5: Commit**

```bash
git add src/equipos/infrastructure/ src/solicitudes/infrastructure/ config/django_settings.py
git commit -m "feat: Django ORM models y repositorios concretos para equipos y solicitudes"
```

---

### Task 10: FastAPI — main, routers, schemas, dependency injection

**Files:**
- Create: `api/main.py`
- Create: `api/routers/equipos.py`
- Create: `api/routers/solicitudes.py`
- Create: `api/routers/borradores.py`
- Create: `config/dependencies.py`
- Create: `tests/e2e/test_flujo_garantia.py`

- [ ] **Step 1: Escribir test e2e que falla**

```python
# tests/e2e/test_flujo_garantia.py
import pytest
from httpx import AsyncClient
from api.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_registrar_equipo_y_consultar():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/equipos/", json={
            "serial": "KYO-TEST-001",
            "nombre": "Kyocera Test",
            "marca": "Kyocera",
            "modelo": "TASKalfa 2553ci",
            "tipo": "multifuncional_impresion",
            "ubicacion_fisica": "Piso 1",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["serial"] == "KYO-TEST-001"

        response2 = await client.get("/equipos/")
        assert response2.status_code == 200
        equipos = response2.json()
        assert any(e["serial"] == "KYO-TEST-001" for e in equipos)
```

- [ ] **Step 2: Ejecutar test para verificar que falla**

```bash
uv run pytest tests/e2e/test_flujo_garantia.py -v
```
Expected: FAIL

- [ ] **Step 3: Implementar api/main.py**

```python
# api/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.database import setup_django
from api.routers import equipos, solicitudes, borradores, agente, notificaciones


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_django()
    yield


app = FastAPI(title="Datecsa Garantías POC", lifespan=lifespan)

app.include_router(equipos.router, prefix="/equipos", tags=["equipos"])
app.include_router(solicitudes.router, prefix="/solicitudes", tags=["solicitudes"])
app.include_router(borradores.router, prefix="/borradores", tags=["borradores"])
app.include_router(agente.router, prefix="/agente", tags=["agente"])
app.include_router(notificaciones.router, prefix="/notificaciones", tags=["notificaciones"])
```

- [ ] **Step 4: Implementar config/dependencies.py**

```python
# config/dependencies.py
from functools import lru_cache
from config.settings import settings
from src.equipos.infrastructure.repositories import DjangoEquipoRepository, DjangoGarantiaRepository
from src.solicitudes.infrastructure.repositories import DjangoSolicitudRepository
from src.agente.infrastructure.email.fake_email_adapter import FakeEmailAdapter
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter
from src.agente.infrastructure.embeddings.fake_embedding_adapter import FakeEmbeddingAdapter
from src.agente.infrastructure.ocr.fake_ocr_adapter import FakeOCRAdapter


def get_equipo_repo() -> DjangoEquipoRepository:
    return DjangoEquipoRepository()


def get_garantia_repo() -> DjangoGarantiaRepository:
    return DjangoGarantiaRepository()


def get_solicitud_repo() -> DjangoSolicitudRepository:
    return DjangoSolicitudRepository()


def get_email_adapter():
    return FakeEmailAdapter()


def get_llm_adapter():
    if settings.LLM_PROVIDER == "gemini":
        from src.agente.infrastructure.llm.gemini_llm_adapter import GeminiLLMAdapter
        return GeminiLLMAdapter(api_key=settings.GEMINI_API_KEY)
    return FakeLLMAdapter()


def get_embedding_adapter():
    if settings.EMBEDDING_PROVIDER == "gemini":
        from src.agente.infrastructure.embeddings.gemini_embedding_adapter import GeminiEmbeddingAdapter
        return GeminiEmbeddingAdapter(api_key=settings.GEMINI_API_KEY, dim=settings.EMBEDDING_DIM)
    return FakeEmbeddingAdapter(dim=settings.EMBEDDING_DIM)
```

- [ ] **Step 5: Implementar api/routers/equipos.py**

```python
# api/routers/equipos.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.equipos.domain.entities import TipoEquipo
from src.equipos.application.registrar_equipo import RegistrarEquipo
from config.dependencies import get_equipo_repo, get_garantia_repo

router = APIRouter()


class EquipoCreate(BaseModel):
    serial: str
    nombre: str
    marca: str
    modelo: str
    tipo: TipoEquipo
    ubicacion_fisica: str


class EquipoResponse(BaseModel):
    serial: str
    nombre: str
    marca: str
    modelo: str
    tipo: TipoEquipo
    ubicacion_fisica: str
    estado: str


@router.post("/", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED)
def registrar_equipo(
    data: EquipoCreate,
    repo=Depends(get_equipo_repo),
):
    caso_uso = RegistrarEquipo(equipo_repo=repo)
    try:
        equipo = caso_uso.execute(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return EquipoResponse(**equipo.__dict__)


@router.get("/", response_model=list[EquipoResponse])
def listar_equipos(repo=Depends(get_equipo_repo)):
    return [EquipoResponse(**e.__dict__) for e in repo.find_all()]
```

- [ ] **Step 6: Implementar api/routers/borradores.py**

```python
# api/routers/borradores.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from config.dependencies import get_email_adapter
from src.seguimiento.infrastructure.repositories import DjangoBorradorCorreoRepository
from src.seguimiento.application.aprobar_borrador import AprobarBorrador
from src.seguimiento.application.rechazar_borrador import RechazarBorrador

router = APIRouter()


class AprobarRequest(BaseModel):
    aprobado_por: str


class RechazarRequest(BaseModel):
    motivo: str


class EditarBorradorRequest(BaseModel):
    cuerpo: str


class BorradorResponse(BaseModel):
    id: str
    solicitud_id: str
    destinatario_email: str
    asunto: str
    cuerpo: str
    estado: str
    aprobado_por: Optional[str] = None


def get_borrador_repo():
    return DjangoBorradorCorreoRepository()


@router.get("/", response_model=list[BorradorResponse])
def listar_pendientes(repo=Depends(get_borrador_repo)):
    borradores = repo.find_pendientes()
    return [BorradorResponse(**b.__dict__) for b in borradores]


@router.patch("/{borrador_id}")
def editar_borrador(borrador_id: str, data: EditarBorradorRequest, repo=Depends(get_borrador_repo)):
    borrador = repo.find_by_id(borrador_id)
    if not borrador:
        raise HTTPException(status_code=404, detail="borrador no encontrado")
    borrador.cuerpo = data.cuerpo
    repo.save(borrador)
    return {"ok": True}


@router.post("/{borrador_id}/aprobar")
def aprobar_borrador(
    borrador_id: str,
    data: AprobarRequest,
    repo=Depends(get_borrador_repo),
    email_adapter=Depends(get_email_adapter),
):
    caso_uso = AprobarBorrador(borrador_repo=repo, email_adapter=email_adapter)
    try:
        caso_uso.execute(borrador_id=borrador_id, aprobado_por=data.aprobado_por)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "mensaje": "Correo enviado"}


@router.post("/{borrador_id}/rechazar")
def rechazar_borrador(
    borrador_id: str,
    data: RechazarRequest,
    repo=Depends(get_borrador_repo),
):
    caso_uso = RechazarBorrador(borrador_repo=repo)
    try:
        caso_uso.execute(borrador_id=borrador_id, motivo=data.motivo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "mensaje": "Borrador rechazado"}
```

- [ ] **Step 7: Verificar que los e2e tests pasan**

```bash
docker compose up -d db
make migrate
uv run pytest tests/e2e/ -v
```
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add api/ config/dependencies.py
git commit -m "feat: FastAPI con routers equipos, solicitudes y borradores (human-in-the-loop)"
```

---

## Sprint 5 — Pipeline del Agente (100% mockeado)

### Task 11: Fake adapters para OCR, LLM, Embeddings y Email

**Files:**
- Create: `src/agente/infrastructure/ocr/fake_ocr_adapter.py`
- Create: `src/agente/infrastructure/llm/fake_llm_adapter.py`
- Create: `src/agente/infrastructure/embeddings/fake_embedding_adapter.py`
- Create: `src/agente/infrastructure/email/fake_email_adapter.py`
- Create: `src/agente/domain/entities.py`

- [ ] **Step 1: Implementar src/agente/domain/entities.py**

```python
# src/agente/domain/entities.py
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Accion(str, Enum):
    CREAR_SOLICITUD = "crear_solicitud"
    ACTUALIZAR_ESTADO = "actualizar_estado"
    NOTIFICAR = "notificar"
    ESCALAR = "escalar"
    IGNORAR = "ignorar"


@dataclass
class DecisionAgente:
    accion: Accion
    confianza: float
    parametros: dict[str, Any] = field(default_factory=dict)
    razonamiento: str = ""
```

- [ ] **Step 2: Implementar fake adapters**

```python
# src/agente/infrastructure/ocr/fake_ocr_adapter.py
from src.agente.domain.ports import OCRPort

FAKE_OCR_TEXT = """
ACTA DE ENTREGA — DATECSA S.A.
Fecha: 2026-04-30
Equipo: Kyocera TASKalfa 2553ci
Serial: KYO-TASKalfa-2021-001
Falla reportada: Error de fusor C3100. El equipo presenta falla en el módulo de
fusión y detiene la impresión a los 5 minutos de operación continua.
Técnico responsable: Carlos Ramírez
Ubicación: Piso 3 - Área Administrativa
"""


class FakeOCRAdapter(OCRPort):
    def __init__(self, texto_fijo: str = FAKE_OCR_TEXT):
        self._texto = texto_fijo

    def extract_text(self, pdf_path: str) -> str:
        return self._texto
```

```python
# src/agente/infrastructure/llm/fake_llm_adapter.py
from src.agente.domain.ports import LLMPort
from src.agente.domain.entities import DecisionAgente, Accion


class FakeLLMAdapter(LLMPort):
    def decide(self, context: str) -> DecisionAgente:
        return DecisionAgente(
            accion=Accion.CREAR_SOLICITUD,
            confianza=0.99,
            parametros={
                "equipo_serial": "KYO-TASKalfa-2021-001",
                "descripcion_falla": "Error de fusor C3100",
                "reportado_por": "Carlos Ramírez",
            },
            razonamiento="[FAKE] Documento contiene acta de entrega con falla de equipo",
        )

    def generate_email(self, context: str) -> dict[str, str]:
        return {
            "asunto": "[FAKE] Seguimiento garantía — Equipo Kyocera TASKalfa 2553ci",
            "cuerpo": (
                "Estimados,\n\nLes escribimos para solicitar amablemente una actualización "
                "sobre el estado del equipo Kyocera TASKalfa 2553ci (Serial: KYO-TASKalfa-2021-001) "
                "que fue entregado para reparación bajo garantía hace más de 7 días.\n\n"
                "Quedamos atentos a su respuesta.\n\nCordialmente,\nDatacsa S.A."
            ),
        }
```

```python
# src/agente/infrastructure/embeddings/fake_embedding_adapter.py
from src.agente.domain.ports import EmbeddingPort


class FakeEmbeddingAdapter(EmbeddingPort):
    def __init__(self, dim: int = 768):
        self._dim = dim

    def embed(self, text: str) -> list[float]:
        return [0.1] * self._dim
```

```python
# src/agente/infrastructure/email/fake_email_adapter.py
from src.agente.domain.ports import EmailPort


class FakeEmailAdapter(EmailPort):
    def __init__(self):
        self.sent: list[dict] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})
```

- [ ] **Step 3: Añadir ports faltantes a src/agente/domain/ports.py**

```python
# src/agente/domain/ports.py
from abc import ABC, abstractmethod
from src.agente.domain.entities import DecisionAgente


class OCRPort(ABC):
    @abstractmethod
    def extract_text(self, pdf_path: str) -> str: ...


class LLMPort(ABC):
    @abstractmethod
    def decide(self, context: str) -> DecisionAgente: ...

    @abstractmethod
    def generate_email(self, context: str) -> dict[str, str]: ...


class EmbeddingPort(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]: ...


class EmailPort(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> None: ...
```

- [ ] **Step 4: Commit**

```bash
git add src/agente/
git commit -m "feat: fake adapters para OCR, LLM, embeddings y email — pipeline mockeado"
```

---

### Task 12: Caso de uso ProcesarDocumento + endpoint /agente/procesar-documento

**Files:**
- Create: `src/agente/application/procesar_documento.py`
- Create: `src/agente/infrastructure/chunking.py`
- Create: `api/routers/agente.py`
- Create: `tests/application/test_procesar_documento.py`

- [ ] **Step 1: Escribir test que falla**

```python
# tests/application/test_procesar_documento.py
from src.agente.application.procesar_documento import ProcesarDocumento
from src.agente.infrastructure.ocr.fake_ocr_adapter import FakeOCRAdapter
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter
from src.agente.infrastructure.embeddings.fake_embedding_adapter import FakeEmbeddingAdapter
from src.solicitudes.application.crear_solicitud import CrearSolicitud
from tests.application.fakes import FakeSolicitudRepository, FakeGarantiaRepository, FakeEquipoRepository
from src.equipos.domain.entities import Equipo, Garantia, TipoEquipo
from datetime import date, timedelta


def _setup_equipo_con_garantia():
    equipo_repo = FakeEquipoRepository()
    garantia_repo = FakeGarantiaRepository()
    equipo = Equipo(serial="KYO-TASKalfa-2021-001", nombre="Kyocera", marca="Kyocera",
                    modelo="TASKalfa", tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION, ubicacion_fisica="Piso 3")
    equipo_repo.save(equipo)
    garantia = Garantia(equipo_id="KYO-TASKalfa-2021-001", proveedor_id="prov-1",
                        fecha_inicio=date.today() - timedelta(days=30),
                        fecha_fin=date.today() + timedelta(days=335), tipo_cobertura="Total")
    garantia_repo.save(garantia)
    return equipo_repo, garantia_repo


def test_procesar_documento_crea_solicitud():
    equipo_repo, garantia_repo = _setup_equipo_con_garantia()
    solicitud_repo = FakeSolicitudRepository()

    caso_uso = ProcesarDocumento(
        ocr=FakeOCRAdapter(),
        llm=FakeLLMAdapter(),
        embedding=FakeEmbeddingAdapter(),
        crear_solicitud=CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo),
    )

    resultado = caso_uso.execute(pdf_path="fixtures/pdfs/acta_entrega_kyocera_001.pdf")

    assert resultado.accion == "crear_solicitud"
    solicitudes = solicitud_repo.find_all()
    assert len(solicitudes) == 1
    assert "C3100" in solicitudes[0].descripcion_falla
```

- [ ] **Step 2: Ejecutar test para verificar que falla**

```bash
uv run pytest tests/application/test_procesar_documento.py -v
```
Expected: FAIL

- [ ] **Step 3: Implementar ChunkingService y ProcesarDocumento**

```python
# src/agente/infrastructure/chunking.py
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    index: int
    metadata: dict


class ChunkingService:
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, text: str, metadata: dict | None = None) -> list[Chunk]:
        metadata = metadata or {}
        words = text.split()
        chunks = []
        start = 0
        index = 0
        while start < len(words):
            end = min(start + self._chunk_size, len(words))
            chunk_text = " ".join(words[start:end])
            chunks.append(Chunk(text=chunk_text, index=index, metadata={**metadata, "chunk_index": index}))
            start += self._chunk_size - self._overlap
            index += 1
        return chunks
```

```python
# src/agente/application/procesar_documento.py
from src.agente.domain.ports import OCRPort, LLMPort, EmbeddingPort
from src.agente.domain.entities import DecisionAgente
from src.agente.infrastructure.chunking import ChunkingService
from src.solicitudes.application.crear_solicitud import CrearSolicitud


class ProcesarDocumento:
    def __init__(
        self,
        ocr: OCRPort,
        llm: LLMPort,
        embedding: EmbeddingPort,
        crear_solicitud: CrearSolicitud,
        chunk_size: int = 800,
        overlap: int = 100,
    ):
        self._ocr = ocr
        self._llm = llm
        self._embedding = embedding
        self._crear_solicitud = crear_solicitud
        self._chunker = ChunkingService(chunk_size=chunk_size, overlap=overlap)

    def execute(self, pdf_path: str) -> DecisionAgente:
        texto = self._ocr.extract_text(pdf_path)
        chunks = self._chunker.chunk(texto, metadata={"pdf_path": pdf_path})
        for chunk in chunks:
            self._embedding.embed(chunk.text)

        decision = self._llm.decide(context=texto)

        if decision.accion.value == "crear_solicitud":
            params = decision.parametros
            self._crear_solicitud.execute(
                equipo_id=params.get("equipo_serial", ""),
                reportado_por=params.get("reportado_por", "Agente OCR"),
                descripcion_falla=params.get("descripcion_falla", texto[:500]),
            )

        return decision
```

- [ ] **Step 4: Implementar api/routers/agente.py**

```python
# api/routers/agente.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from config.dependencies import get_llm_adapter, get_embedding_adapter, get_solicitud_repo, get_garantia_repo
from src.agente.infrastructure.ocr.fake_ocr_adapter import FakeOCRAdapter
from src.agente.application.procesar_documento import ProcesarDocumento
from src.solicitudes.application.crear_solicitud import CrearSolicitud

router = APIRouter()


class ProcesarDocumentoRequest(BaseModel):
    pdf_path: str


@router.post("/procesar-documento")
def procesar_documento(
    data: ProcesarDocumentoRequest,
    llm=Depends(get_llm_adapter),
    embedding=Depends(get_embedding_adapter),
    solicitud_repo=Depends(get_solicitud_repo),
    garantia_repo=Depends(get_garantia_repo),
):
    crear_solicitud = CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo)
    caso_uso = ProcesarDocumento(
        ocr=FakeOCRAdapter(),
        llm=llm,
        embedding=embedding,
        crear_solicitud=crear_solicitud,
    )
    decision = caso_uso.execute(pdf_path=data.pdf_path)
    return {"accion": decision.accion, "confianza": decision.confianza, "razonamiento": decision.razonamiento}
```

- [ ] **Step 5: Verificar que los tests pasan**

```bash
uv run pytest tests/application/test_procesar_documento.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/agente/application/ src/agente/infrastructure/chunking.py api/routers/agente.py tests/application/test_procesar_documento.py
git commit -m "feat: pipeline agente mockeado — procesar documento PDF end-to-end"
```

---

## Sprint 6 — Seguimiento semanal y escalamiento

### Task 13: VerificarEstadoSemanal + EscalarSolicitud

**Files:**
- Create: `src/seguimiento/application/verificar_estado_semanal.py`
- Create: `src/seguimiento/application/escalar_solicitud.py`
- Create: `tests/application/test_verificar_estado_semanal.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/application/test_verificar_estado_semanal.py
from datetime import date, timedelta, datetime
from src.seguimiento.application.verificar_estado_semanal import VerificarEstadoSemanal
from src.seguimiento.domain.entities import EstadoBorrador, DestinatarioTipo
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.trazabilidad.domain.entities import EventoTrazabilidad, MetodoRegistro
from tests.application.fakes import (
    FakeSolicitudRepository, FakeTrazabilidadRepository,
    FakeBorradorCorreoRepository, FakeEventoSeguimientoRepository,
)
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter


def _solicitud_despachada_hace_n_dias(n: int) -> SolicitudGarantia:
    s = SolicitudGarantia(
        equipo_id="KYO-001", garantia_id="g-1",
        reportado_por="Carlos", descripcion_falla="Falla fusor"
    )
    s.validar()
    s.despachar()
    return s


def _evento_hace_n_dias(solicitud_id: str, n: int) -> EventoTrazabilidad:
    return EventoTrazabilidad(
        equipo_id="KYO-001", solicitud_id=solicitud_id,
        ubicacion_anterior="Almacén", ubicacion_nueva="Proveedor Kyocera",
        responsable="Carlos", metodo_registro=MetodoRegistro.MANUAL,
        timestamp=datetime.now() - timedelta(days=n),
    )


def test_genera_borrador_cuando_timeout_superado():
    solicitud_repo = FakeSolicitudRepository()
    trazabilidad_repo = FakeTrazabilidadRepository()
    borrador_repo = FakeBorradorCorreoRepository()
    seguimiento_repo = FakeEventoSeguimientoRepository()

    solicitud = _solicitud_despachada_hace_n_dias(8)
    solicitud_repo.save(solicitud)
    evento = _evento_hace_n_dias(solicitud.id, 8)
    trazabilidad_repo.save(evento)

    caso_uso = VerificarEstadoSemanal(
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=trazabilidad_repo,
        borrador_repo=borrador_repo,
        seguimiento_repo=seguimiento_repo,
        llm=FakeLLMAdapter(),
        timeout_proveedor_dias=7,
        proveedor_email="soporte@kyocera.co",
    )
    caso_uso.execute()

    borradores = borrador_repo.find_pendientes()
    assert len(borradores) == 1
    assert borradores[0].destinatario_tipo == DestinatarioTipo.PROVEEDOR
    assert borradores[0].estado == EstadoBorrador.PENDIENTE_APROBACION


def test_no_genera_borrador_si_ya_hay_uno_pendiente():
    solicitud_repo = FakeSolicitudRepository()
    trazabilidad_repo = FakeTrazabilidadRepository()
    borrador_repo = FakeBorradorCorreoRepository()
    seguimiento_repo = FakeEventoSeguimientoRepository()

    solicitud = _solicitud_despachada_hace_n_dias(10)
    solicitud_repo.save(solicitud)
    trazabilidad_repo.save(_evento_hace_n_dias(solicitud.id, 10))

    caso_uso = VerificarEstadoSemanal(
        solicitud_repo=solicitud_repo, trazabilidad_repo=trazabilidad_repo,
        borrador_repo=borrador_repo, seguimiento_repo=seguimiento_repo,
        llm=FakeLLMAdapter(), timeout_proveedor_dias=7,
        proveedor_email="soporte@kyocera.co",
    )
    caso_uso.execute()
    caso_uso.execute()  # segunda ejecución — idempotente

    assert len(borrador_repo.find_pendientes()) == 1
```

- [ ] **Step 2: Ejecutar tests para verificar que fallan**

```bash
uv run pytest tests/application/test_verificar_estado_semanal.py -v
```
Expected: FAIL

- [ ] **Step 3: Implementar VerificarEstadoSemanal**

```python
# src/seguimiento/application/verificar_estado_semanal.py
from datetime import datetime, timedelta
from src.solicitudes.domain.ports import SolicitudRepository
from src.solicitudes.domain.entities import EstadoSolicitud
from src.trazabilidad.domain.ports import TrazabilidadRepository
from src.seguimiento.domain.ports import BorradorCorreoRepository, EventoSeguimientoRepository
from src.seguimiento.domain.entities import (
    BorradorCorreo, EventoSeguimiento, DestinatarioTipo, EstadoBorrador
)
from src.agente.domain.ports import LLMPort


class VerificarEstadoSemanal:
    def __init__(
        self,
        solicitud_repo: SolicitudRepository,
        trazabilidad_repo: TrazabilidadRepository,
        borrador_repo: BorradorCorreoRepository,
        seguimiento_repo: EventoSeguimientoRepository,
        llm: LLMPort,
        timeout_proveedor_dias: int = 7,
        proveedor_email: str = "",
    ):
        self._solicitudes = solicitud_repo
        self._trazabilidad = trazabilidad_repo
        self._borradores = borrador_repo
        self._seguimiento = seguimiento_repo
        self._llm = llm
        self._timeout = timeout_proveedor_dias
        self._proveedor_email = proveedor_email

    def execute(self) -> None:
        estados_activos = [EstadoSolicitud.DESPACHADA, EstadoSolicitud.EN_REPARACION]
        for estado in estados_activos:
            for solicitud in self._solicitudes.find_by_estado(estado):
                self._verificar_solicitud(solicitud)

    def _verificar_solicitud(self, solicitud) -> None:
        ultimo_evento = self._trazabilidad.find_ultimo_evento(solicitud.id)
        if not ultimo_evento:
            return

        dias_sin_respuesta = (datetime.now() - ultimo_evento.timestamp).days

        evento = EventoSeguimiento(
            solicitud_id=solicitud.id,
            tipo_evento="verificacion_semanal",
            descripcion=f"Verificación semanal: {dias_sin_respuesta} días sin respuesta",
            dias_sin_respuesta=dias_sin_respuesta,
        )
        self._seguimiento.save(evento)

        if dias_sin_respuesta < self._timeout:
            return

        borrador_existente = self._borradores.find_by_solicitud_y_estado(
            solicitud.id, EstadoBorrador.PENDIENTE_APROBACION
        )
        if borrador_existente:
            return

        contexto = (
            f"Solicitud {solicitud.id} para equipo {solicitud.equipo_id}. "
            f"Falla: {solicitud.descripcion_falla}. "
            f"Días sin respuesta del proveedor: {dias_sin_respuesta}."
        )
        email_data = self._llm.generate_email(context=contexto)

        borrador = BorradorCorreo(
            solicitud_id=solicitud.id,
            destinatario_tipo=DestinatarioTipo.PROVEEDOR,
            destinatario_email=self._proveedor_email,
            asunto=email_data["asunto"],
            cuerpo=email_data["cuerpo"],
        )
        self._borradores.save(borrador)
```

- [ ] **Step 4: Verificar que los tests pasan**

```bash
uv run pytest tests/application/test_verificar_estado_semanal.py -v
```
Expected: PASS

- [ ] **Step 5: Agregar endpoint /agente/verificar-semanal**

```python
# En api/routers/agente.py — agregar:
from src.seguimiento.application.verificar_estado_semanal import VerificarEstadoSemanal
from config.settings import settings

@router.post("/verificar-semanal")
def verificar_estado_semanal(
    llm=Depends(get_llm_adapter),
    solicitud_repo=Depends(get_solicitud_repo),
):
    from src.trazabilidad.infrastructure.repositories import DjangoTrazabilidadRepository
    from src.seguimiento.infrastructure.repositories import DjangoBorradorCorreoRepository, DjangoEventoSeguimientoRepository
    caso_uso = VerificarEstadoSemanal(
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=DjangoTrazabilidadRepository(),
        borrador_repo=DjangoBorradorCorreoRepository(),
        seguimiento_repo=DjangoEventoSeguimientoRepository(),
        llm=llm,
        timeout_proveedor_dias=settings.TIMEOUT_PROVEEDOR_DIAS,
    )
    caso_uso.execute()
    return {"ok": True, "mensaje": "Verificación completada"}
```

- [ ] **Step 6: Commit**

```bash
git add src/seguimiento/ api/routers/agente.py tests/application/test_verificar_estado_semanal.py
git commit -m "feat: verificación semanal idempotente con escalamiento y generación de borradores"
```

---

## Sprint 7 — Gemini real (embeddings + LLM + OCR)

### Task 14: Gemini adapters reales

**Files:**
- Create: `src/agente/infrastructure/embeddings/gemini_embedding_adapter.py`
- Create: `src/agente/infrastructure/llm/gemini_llm_adapter.py`
- Create: `src/agente/infrastructure/ocr/gemini_ocr_adapter.py`
- Create: `src/agente/infrastructure/vector_store.py`

- [ ] **Step 1: Instalar dependencias Gemini**

```bash
uv add google-generativeai
```

- [ ] **Step 2: Implementar GeminiEmbeddingAdapter**

```python
# src/agente/infrastructure/embeddings/gemini_embedding_adapter.py
import google.generativeai as genai
from src.agente.domain.ports import EmbeddingPort
from config.settings import settings


class GeminiEmbeddingAdapter(EmbeddingPort):
    def __init__(self, api_key: str, dim: int = 768):
        genai.configure(api_key=api_key)
        self._dim = dim

    def embed(self, text: str) -> list[float]:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
            output_dimensionality=self._dim,
        )
        return result["embedding"]
```

- [ ] **Step 3: Implementar GeminiLLMAdapter**

```python
# src/agente/infrastructure/llm/gemini_llm_adapter.py
import json
import google.generativeai as genai
from src.agente.domain.ports import LLMPort
from src.agente.domain.entities import DecisionAgente, Accion

_SYSTEM_PROMPT = """
Eres un agente de gestión de garantías de equipos para Datecsa S.A.
Analiza el texto del documento y responde SOLO con JSON válido:
{
  "accion": "crear_solicitud" | "actualizar_estado" | "notificar" | "escalar" | "ignorar",
  "confianza": float 0-1,
  "parametros": {
    "equipo_serial": "...",
    "descripcion_falla": "...",
    "reportado_por": "..."
  },
  "razonamiento": "..."
}
"""


class GeminiLLMAdapter(LLMPort):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-1.5-flash")

    def decide(self, context: str) -> DecisionAgente:
        response = self._model.generate_content(f"{_SYSTEM_PROMPT}\n\nDocumento:\n{context}")
        data = json.loads(response.text.strip().strip("```json").strip("```"))
        return DecisionAgente(
            accion=Accion(data["accion"]),
            confianza=data["confianza"],
            parametros=data.get("parametros", {}),
            razonamiento=data.get("razonamiento", ""),
        )

    def generate_email(self, context: str) -> dict[str, str]:
        prompt = (
            f"Genera un correo formal y amable en español para solicitar una actualización "
            f"de garantía. Contexto: {context}\n"
            f"Responde SOLO con JSON: {{\"asunto\": \"...\", \"cuerpo\": \"...\"}}"
        )
        response = self._model.generate_content(prompt)
        return json.loads(response.text.strip().strip("```json").strip("```"))
```

- [ ] **Step 4: Implementar vector store pgvector**

```python
# src/agente/infrastructure/vector_store.py
from django.db import connection
from src.agente.infrastructure.chunking import Chunk
import json


def store_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS document_chunks ("
            "id SERIAL PRIMARY KEY, text TEXT, embedding vector(768), metadata JSONB)"
        )
        for chunk, embedding in zip(chunks, embeddings):
            cursor.execute(
                "INSERT INTO document_chunks (text, embedding, metadata) VALUES (%s, %s::vector, %s)",
                [chunk.text, str(embedding), json.dumps(chunk.metadata)],
            )


def search_similar(query_embedding: list[float], limit: int = 5) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT text, metadata, 1 - (embedding <=> %s::vector) AS similarity "
            "FROM document_chunks ORDER BY embedding <=> %s::vector LIMIT %s",
            [str(query_embedding), str(query_embedding), limit],
        )
        rows = cursor.fetchall()
    return [{"text": r[0], "metadata": r[1], "similarity": r[2]} for r in rows]
```

- [ ] **Step 5: Commit**

```bash
git add src/agente/infrastructure/
git commit -m "feat: Gemini adapters reales — embeddings Matryoshka 768, LLM decisor, pgvector store"
```

---

## Sprint 8 — PDFs sintéticos Datecsa

### Task 15: Generar fixtures PDF con datos reales Datecsa

**Files:**
- Create: `scripts/generate_fixtures.py`
- Create: `fixtures/equipos.json`
- Create: `fixtures/proveedores.json`

- [ ] **Step 1: Instalar reportlab**

```bash
uv add reportlab
```

- [ ] **Step 2: Implementar generate_fixtures.py**

```python
# scripts/generate_fixtures.py
import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

FIXTURES_DIR = Path("fixtures")
PDFS_DIR = FIXTURES_DIR / "pdfs"
PDFS_DIR.mkdir(parents=True, exist_ok=True)

EQUIPOS = [
    {"serial": "KYO-TASKalfa-2021-001", "marca": "Kyocera", "modelo": "TASKalfa 2553ci",
     "tipo": "multifuncional_impresion", "ubicacion": "Piso 3 - Área Administrativa"},
    {"serial": "BAR-CS-2022-014", "marca": "Barco", "modelo": "ClickShare CX-50",
     "tipo": "colaboracion_audiovisual", "ubicacion": "Sala de Juntas Principal"},
    {"serial": "BSP-PMX-2020-007", "marca": "Bose Professional", "modelo": "PowerMatch PM8500N",
     "tipo": "audio_corporativo", "ubicacion": "Auditorio"},
    {"serial": "CRE-TSW-2023-003", "marca": "Crestron", "modelo": "TSW-770",
     "tipo": "automatizacion_sala", "ubicacion": "Sala Ejecutiva B"},
    {"serial": "LG-MRI-2022-021", "marca": "LG Business", "modelo": "55SM5KE",
     "tipo": "senalizacion_digital", "ubicacion": "Recepción Principal"},
]

FALLAS = [
    ("KYO-TASKalfa-2021-001", "Carlos Ramírez", "soporte@kyocera.co",
     "Error de fusor C3100. El equipo muestra código C3100 y detiene impresión a los 5 minutos.",
     "Afecta área administrativa con 40+ usuarios. Urgente para operación diaria."),
    ("BAR-CS-2022-014", "Ana Gómez", "soporte@barco.com",
     "Botón ClickShare no establece conexión con pantalla principal. WiFi conectado, sin video.",
     "Sala de juntas inutilizable. Afecta reuniones ejecutivas diarias."),
    ("BSP-PMX-2020-007", "Luis Torres", "soporte@bose.com",
     "Canales 3 y 4 del amplificador sin señal de salida. Canales 1, 2, 5-8 funcionan.",
     "Detectado durante evento corporativo con 200 asistentes. Sistema de audio crítico."),
    ("CRE-TSW-2023-003", "María Castro", "soporte@crestron.com",
     "Panel táctil TSW-770 no responde al toque. Pantalla enciende pero no registra input.",
     "Sala ejecutiva sin control de luces, cortinas y videoconferencia."),
    ("LG-MRI-2022-021", "Pedro Silva", "soporte@lg.com",
     "Monitor industrial con banda horizontal de píxeles muertos a 30cm del borde superior.",
     "Señalización digital de recepción afectada. Impacto en imagen corporativa."),
]


def generar_acta_pdf(serial: str, tecnico: str, proveedor_email: str, falla: str, situacion: str) -> str:
    equipo = next(e for e in EQUIPOS if e["serial"] == serial)
    filename = PDFS_DIR / f"acta_entrega_{serial.replace('-', '_').lower()}.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>DATECSA S.A.</b>", styles["Title"]))
    story.append(Paragraph("ACTA DE ENTREGA — GARANTÍA DE EQUIPO", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"<b>Fecha:</b> 2026-04-30", styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("<b>DATOS DEL EQUIPO</b>", styles["Heading3"]))
    story.append(Paragraph(f"Serial: {serial}", styles["Normal"]))
    story.append(Paragraph(f"Marca: {equipo['marca']}", styles["Normal"]))
    story.append(Paragraph(f"Modelo: {equipo['modelo']}", styles["Normal"]))
    story.append(Paragraph(f"Tipo: {equipo['tipo']}", styles["Normal"]))
    story.append(Paragraph(f"Ubicación: {equipo['ubicacion']}", styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("<b>DESCRIPCIÓN DE LA FALLA</b>", styles["Heading3"]))
    story.append(Paragraph(falla, styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("<b>SITUACIÓN Y CONTEXTO</b>", styles["Heading3"]))
    story.append(Paragraph(situacion, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"<b>Técnico responsable:</b> {tecnico}", styles["Normal"]))
    story.append(Paragraph(f"<b>Proveedor destino:</b> {proveedor_email}", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Firma técnico: ____________________", styles["Normal"]))
    story.append(Paragraph("Firma recepción: ____________________", styles["Normal"]))

    doc.build(story)
    print(f"  ✓ {filename}")
    return str(filename)


def main():
    print("Generando fixtures JSON...")
    (FIXTURES_DIR / "equipos.json").write_text(json.dumps(EQUIPOS, indent=2, ensure_ascii=False))

    proveedores = [
        {"nombre": "Kyocera Document Solutions", "email": "soporte@kyocera.co", "tiempo_respuesta_dias": 5},
        {"nombre": "Barco NV Colombia", "email": "soporte@barco.com", "tiempo_respuesta_dias": 7},
        {"nombre": "Bose Professional", "email": "soporte@bose.com", "tiempo_respuesta_dias": 10},
        {"nombre": "Crestron Electronics", "email": "soporte@crestron.com", "tiempo_respuesta_dias": 7},
        {"nombre": "LG Business Solutions", "email": "soporte@lg.com", "tiempo_respuesta_dias": 5},
    ]
    (FIXTURES_DIR / "proveedores.json").write_text(json.dumps(proveedores, indent=2, ensure_ascii=False))

    print("Generando PDFs sintéticos...")
    for serial, tecnico, email, falla, situacion in FALLAS:
        generar_acta_pdf(serial, tecnico, email, falla, situacion)

    print("Done. Fixtures generados en fixtures/")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Ejecutar generador**

```bash
make fixtures
```
Expected: 5 PDFs generados en `fixtures/pdfs/`

- [ ] **Step 4: Smoke test completo end-to-end**

```bash
make docker-up
# En otra terminal:
make migrate

# Registrar equipo
curl -X POST http://localhost:8000/equipos/ \
  -H "Content-Type: application/json" \
  -d '{"serial":"KYO-TASKalfa-2021-001","nombre":"Kyocera TASKalfa","marca":"Kyocera","modelo":"TASKalfa 2553ci","tipo":"multifuncional_impresion","ubicacion_fisica":"Piso 3"}'

# Procesar PDF
curl -X POST http://localhost:8000/agente/procesar-documento \
  -H "Content-Type: application/json" \
  -d '{"pdf_path":"fixtures/pdfs/acta_entrega_kyo_taskafa_2021_001.pdf"}'

# Verificar solicitud creada
curl http://localhost:8000/solicitudes/

# Ejecutar verificación semanal (simula 8 días después)
curl -X POST http://localhost:8000/agente/verificar-semanal

# Ver borradores pendientes de aprobación
curl http://localhost:8000/borradores/

# Aprobar borrador (human-in-the-loop)
curl -X POST http://localhost:8000/borradores/{id}/aprobar \
  -H "Content-Type: application/json" \
  -d '{"aprobado_por":"juan@datecsa.com"}'
```

Expected: flujo completo funcional

- [ ] **Step 5: Commit final**

```bash
git add scripts/ fixtures/
git commit -m "feat: fixtures PDF sintéticos con datos reales Datecsa — demo end-to-end completo"
```

---

## Verificación final

```bash
# Suite completa
make test

# Levantar para demo
make docker-up
make migrate
make fixtures
```

Swagger UI disponible en: `http://localhost:8000/docs`
