# Datecsa Garantías — POC Backend

## Contexto del proyecto

**Empresa:** Datecsa S.A., Cali, Colombia. 34 años de experiencia. Distribuidor exclusivo de Kyocera en Colombia. Comercializa soluciones audiovisuales (Barco, Crestron, Bose Professional, LG InMedia).

**Problema:** El proceso actual de garantías de equipos tiene tres fallas críticas:
1. Demoras en el servicio por falta de comunicación entre ventas y servicio técnico
2. Todo el flujo ocurre por correo — sin sistema, sin dueño claro del proceso
3. Sin trazabilidad: se pierde el rastro del equipo entre servicio técnico, área administrativa y proveedor

**Solución POC:** Backend funcional que automatiza el flujo end-to-end con un agente de IA que procesa documentos físicos (PDFs/actas) y correos, extrae información y los convierte en acciones del sistema.

**Objetivo de la demo:** Mostrar el flujo completo: PDF de acta → OCR → agente decide → solicitud creada → trazabilidad actualizada → notificación enviada.

---

## Stack tecnológico

| Herramienta | Rol |
|-------------|-----|
| Python | Lenguaje principal |
| FastAPI | API HTTP |
| Django ORM | Repository pattern (standalone, sin servidor Django) |
| Pydantic + pydantic-settings | Validación de datos y configuración desde `.env` |
| PostgreSQL + pgvector | Persistencia + búsqueda vectorial semántica |
| Gemini text-embedding-004 | Embeddings Matryoshka (dim=768) |
| Gemini (LLM) | Decisiones del agente |
| FakeLLM / FakeEmbedding | Adapters mock para tests (siempre mock primero) |
| uv | Gestión de paquetes y entorno virtual |
| Docker + Docker Compose | Infraestructura local |
| pytest | Tests unitarios, aplicación, integración, e2e |
| reportlab | Generación de PDFs sintéticos con datos Datecsa |

---

## Arquitectura: Hexagonal por módulo

**Principio fundamental:** Cada módulo del dominio tiene sus propias capas hexagonales (`domain → application → infrastructure`). Los módulos se comunican únicamente a través de casos de uso (application layer), nunca directamente entre infraestructuras.

```
[FastAPI routers / EmailAdapter / OCRAdapter]  ← Adapters de entrada (primarios)
                     ↓
           [Application Layer]                 ← Casos de uso — orquestación
                     ↓
            [Domain Layer]                     ← Entidades, reglas de negocio puras
                     ↓
  [Django ORM / pgvector / EmailSender]        ← Adapters de salida (secundarios)
```

**Regla de dependencias:** El dominio no conoce la infraestructura. La infraestructura implementa los puertos (interfaces) definidos en el dominio.

---

## Estructura del proyecto

```
garantias_poc/
├── src/
│   ├── shared/
│   │   ├── domain/          # BaseEntity, DomainEvent, ValueObject base
│   │   └── infrastructure/  # Configuración DB, setup pgvector
│   │
│   ├── equipos/
│   │   ├── domain/          # Equipo, Garantia, value objects
│   │   ├── application/     # RegistrarEquipo, VerificarGarantia (casos de uso)
│   │   └── infrastructure/  # Django ORM models, repositorios concretos
│   │
│   ├── solicitudes/
│   │   ├── domain/          # SolicitudGarantia, ActaEntrega, estados
│   │   ├── application/     # CrearSolicitud, ActualizarEstado, CerrarGarantia
│   │   └── infrastructure/  # Repositorios concretos
│   │
│   ├── trazabilidad/
│   │   ├── domain/          # UbicacionEquipo, EventoTrazabilidad
│   │   ├── application/     # RegistrarMovimiento, ConsultarUbicacion
│   │   └── infrastructure/  # Persistencia
│   │
│   ├── seguimiento/
│   │   ├── domain/          # BorradorCorreo, EventoSeguimiento, estados
│   │   ├── application/     # VerificarEstadoSemanal, EscalarSolicitud, AprobarBorrador, RechazarBorrador
│   │   └── infrastructure/  # Repositorios, integración con EmailAdapter
│   │
│   ├── agente/
│   │   ├── domain/          # DecisionAgente, Accion, Contexto
│   │   ├── application/     # ProcesarEntrada, EjecutarDecision
│   │   └── infrastructure/
│   │       ├── ocr/         # ocr_port.py | fake_ocr_adapter.py | gemini_ocr_adapter.py
│   │       ├── llm/         # llm_port.py | fake_llm_adapter.py | gemini_llm_adapter.py
│   │       ├── embeddings/  # embedding_port.py | fake_embedding_adapter.py | gemini_embedding_adapter.py
│   │       └── email/       # email_port.py | fake_email_adapter.py | office365_adapter.py
│   │
│   └── notificaciones/
│       ├── domain/          # Notificacion, Destinatario
│       ├── application/     # EnviarNotificacion
│       └── infrastructure/  # EmailSender mock, plantillas
│
├── api/
│   ├── routers/
│   │   ├── equipos.py
│   │   ├── garantias.py
│   │   ├── solicitudes.py
│   │   ├── trazabilidad.py
│   │   ├── agente.py
│   │   └── notificaciones.py
│   └── main.py
│
├── config/
│   ├── settings.py          # Pydantic BaseSettings — fuente única de configuración
│   ├── database.py          # Django ORM standalone (django.setup() sin servidor)
│   └── dependencies.py      # FastAPI dependency injection (repositorios, adapters)
│
├── tests/
│   ├── unit/                # Dominio puro — sin DB, sin mocks externos
│   ├── application/         # Casos de uso con FakeRepository en memoria
│   ├── integration/         # Repositorios Django + pgvector contra PostgreSQL real
│   └── e2e/                 # Flujo HTTP completo con TestClient de FastAPI
│
├── fixtures/
│   ├── pdfs/                # PDFs sintéticos generados con datos Datecsa reales
│   ├── equipos.json
│   ├── garantias.json
│   ├── solicitudes.json
│   ├── ordenes_servicio.json
│   └── proveedores.json
│
├── scripts/
│   └── generate_fixtures.py # Genera PDFs + JSON con equipos y fallas reales de Datecsa
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml           # uv — gestión de dependencias
├── .env.example
└── CLAUDE.md                # este archivo
```

---

## Configuración centralizada

**Principio:** Todo comportamiento configurable vive en `config/settings.py`. Nunca hardcodear valores de conexión, claves o proveedores en el código.

### config/settings.py

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str

    # LLM
    LLM_PROVIDER: str = "fake"        # "fake" | "gemini"
    GEMINI_API_KEY: str = ""

    # Embeddings
    EMBEDDING_PROVIDER: str = "fake"  # "fake" | "gemini"
    EMBEDDING_DIM: int = 768          # Matryoshka — no cambiar sin migrar pgvector

    # OCR
    OCR_BACKEND: str = "mock"         # "mock" | "gemini_vision"

    # Email
    EMAIL_BACKEND: str = "mock"       # "mock" | "office365"
    EMAIL_HOST: str = ""

    # Escalamiento y seguimiento
    TIMEOUT_PROVEEDOR_DIAS: int = 7   # días calendario sin respuesta del proveedor
    TIMEOUT_CLIENTE_DIAS: int = 7     # días calendario sin respuesta del cliente

    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret"

    class Config:
        env_file = ".env"

settings = Settings()
```

### .env.example

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/garantias
LLM_PROVIDER=fake
GEMINI_API_KEY=
EMBEDDING_PROVIDER=fake
OCR_BACKEND=mock
EMAIL_BACKEND=mock
TIMEOUT_PROVEEDOR_DIAS=7
TIMEOUT_CLIENTE_DIAS=7
DEBUG=true
SECRET_KEY=dev-secret
```

### Selección de adapter en runtime

```python
# config/dependencies.py
def get_llm_adapter() -> LLMPort:
    if settings.LLM_PROVIDER == "gemini":
        return GeminiLLMAdapter(api_key=settings.GEMINI_API_KEY)
    return FakeLLMAdapter()
```

Cada adapter implementa el puerto (interfaz ABC) definido en el dominio del módulo. El código de aplicación solo conoce el puerto, nunca la implementación concreta.

---

## Modelo de dominio

### Entidades

| Entidad | Campos clave | Módulo |
|---------|-------------|--------|
| `Equipo` | serial, nombre, marca, modelo, tipo, ubicacion_fisica, estado | equipos |
| `Garantia` | equipo_id, proveedor_id, fecha_inicio, fecha_fin, tipo_cobertura, estado | equipos |
| `SolicitudGarantia` | equipo_id, garantia_id, reportado_por, descripcion_falla, estado | solicitudes |
| `ActaEntrega` | solicitud_id, tecnico_responsable, fecha_entrega, imagen_acta | solicitudes |
| `EventoTrazabilidad` | equipo_id, solicitud_id, ubicacion_anterior, ubicacion_nueva, metodo_registro | trazabilidad |
| `Proveedor` | nombre, contacto_email, tiempo_respuesta_dias | equipos |
| `Notificacion` | destinatario, tipo, canal, estado, timestamp | notificaciones |
| `BorradorCorreo` | solicitud_id, destinatario_tipo, destinatario_email, asunto, cuerpo, estado, aprobado_por, fecha_aprobacion | seguimiento |
| `EventoSeguimiento` | solicitud_id, tipo_evento, descripcion, fecha, dias_sin_respuesta | seguimiento |

### Estados de SolicitudGarantia

```
nueva → validada → despachada → en_reparacion → devuelta → cerrada
```

### Estados de BorradorCorreo

```
generado → pendiente_aprobacion → aprobado → enviado
                                → rechazado
```

**Regla:** ningún correo sale del sistema sin pasar por `aprobado`. El adapter de email solo puede enviar correos en estado `aprobado`. Si es `rechazado`, el agente puede generar un nuevo borrador.

### Tipos de equipo Datecsa

```python
class TipoEquipo(str, Enum):
    MULTIFUNCIONAL_IMPRESION = "multifuncional_impresion"   # Kyocera TASKalfa, ECOSYS
    IMPRESORA_PRODUCCION = "impresora_produccion"           # OCÉ
    COLABORACION_AUDIOVISUAL = "colaboracion_audiovisual"   # Barco ClickShare
    AUTOMATIZACION_SALA = "automatizacion_sala"             # Crestron TSW
    AUDIO_CORPORATIVO = "audio_corporativo"                 # Bose Professional
    SENALIZACION_DIGITAL = "senalizacion_digital"           # LG Business (InMedia)
    VIDEOCONFERENCIA = "videoconferencia"                   # Equipos Teams/Zoom/Meet
```

---

## Pipeline del Agente IA

### Procesamiento de documentos (PDF → acción)

```
PDF (acta / orden de servicio / orden de garantía)
    ↓
OCRAdapter          → extrae texto (mock: lee directo | real: Gemini Vision)
    ↓
ChunkingService     → chunk_size=800, overlap=100, separators=["\n\n", "\n", ". "]
    ↓
EmbeddingAdapter    → Gemini text-embedding-004 Matryoshka dim=768 (o Fake: [0.1]*768)
    ↓
pgvector            → chunks + embeddings + metadata
                       {doc_type, equipo_serial, solicitud_id, pagina, chunk_index}
    ↓
AgentService        → búsqueda semántica → recupera contexto → LLM decide acción
    ↓
DecisionAgente      → CREAR_SOLICITUD | ACTUALIZAR_ESTADO | NOTIFICAR | ESCALAR
    ↓
Caso de uso         → ejecuta en el módulo correspondiente (nunca acceso directo a DB)
```

### Procesamiento de correo entrante (O365 mock → acción)

```
Correo proveedor (CC a responsable + agente)
    ↓
EmailAdapter        → parsea asunto, cuerpo, adjuntos
    ↓
AgentService        → LLM clasifica: actualización de estado / despacho / cierre
    ↓
EventoTrazabilidad  → registra nueva ubicación del equipo
    ↓
EventoSeguimiento   → registra respuesta recibida, resetea contador de días
    ↓
Notificacion        → notifica área administrativa
```

### Verificación semanal de trazabilidad (agente orquestador)

El agente verifica semanalmente el estado de todas las solicitudes activas. Para cada solicitud calcula los días transcurridos sin respuesta del proveedor o del cliente.

```
VerificarEstadoSemanal (trigger: endpoint manual o scheduler)
    ↓
AgentService        → consulta solicitudes activas con estado despachada | en_reparacion
    ↓
Por cada solicitud:
    calcular dias_sin_respuesta = hoy - ultimo_evento_trazabilidad
    ↓
    si dias_sin_respuesta >= settings.TIMEOUT_PROVEEDOR_DIAS:
        EscalarSolicitud → genera BorradorCorreo para proveedor
    ↓
    si dias_sin_respuesta >= settings.TIMEOUT_CLIENTE_DIAS:
        EscalarSolicitud → genera BorradorCorreo para cliente
    ↓
    EventoSeguimiento  → registra verificación realizada
```

### Human-in-the-loop: aprobación de correos

**Ningún correo se envía automáticamente.** El agente solo genera borradores. Un usuario Datecsa (puede ser diferente por solicitud) revisa y aprueba o rechaza antes del envío.

```
BorradorCorreo generado (estado: pendiente_aprobacion)
    ↓
Usuario Datecsa recibe notificación interna de borrador pendiente
    ↓
Usuario revisa vía endpoint PATCH /borradores/{id}/aprobar o /rechazar
    ↓
    APROBADO → EmailAdapter.send() → estado: enviado → EventoSeguimiento
    RECHAZADO → estado: rechazado → agente puede generar nuevo borrador
```

**Contenido del borrador (generado por LLM):**
- Saludo formal con nombre del proveedor/cliente
- Referencia al equipo: serial, marca, modelo
- Número de solicitud y fecha de despacho
- Días transcurridos sin respuesta (calculado)
- Solicitud amable de feedback o actualización de estado
- Datos de contacto del responsable Datecsa

**El usuario Datecsa puede editar el cuerpo del borrador antes de aprobar** vía `PATCH /borradores/{id}` con el campo `cuerpo`.

### Datos sintéticos Datecsa (fixtures/pdfs/)

PDFs generados con `reportlab` usando formato predefinido: encabezado Datecsa, datos del equipo, descripción de falla, técnico responsable, firma.

Equipos representativos en fixtures:

```json
[
  {"serial": "KYO-TASKalfa-2021-001", "marca": "Kyocera", "modelo": "TASKalfa 2553ci", "tipo": "multifuncional_impresion", "ubicacion": "Piso 3 - Área Administrativa"},
  {"serial": "BAR-CS-2022-014", "marca": "Barco", "modelo": "ClickShare CX-50", "tipo": "colaboracion_audiovisual", "ubicacion": "Sala de Juntas Principal"},
  {"serial": "BSP-PMX-2020-007", "marca": "Bose Professional", "modelo": "PowerMatch PM8500N", "tipo": "audio_corporativo", "ubicacion": "Auditorio"},
  {"serial": "CRE-TSW-2023-003", "marca": "Crestron", "modelo": "TSW-770", "tipo": "automatizacion_sala", "ubicacion": "Sala Ejecutiva B"},
  {"serial": "LG-MRI-2022-021", "marca": "LG Business", "modelo": "55SM5KE", "tipo": "senalizacion_digital", "ubicacion": "Recepción Principal"}
]
```

---

## API FastAPI — Endpoints

```
# Equipos
GET    /equipos/                    → listar equipos con filtros
POST   /equipos/                    → registrar equipo
GET    /equipos/{id}/garantia       → garantía vigente del equipo
GET    /equipos/{id}/trazabilidad   → historial de ubicaciones

# Solicitudes de garantía
POST   /solicitudes/                → crear solicitud manual
GET    /solicitudes/                → listar (filtros: estado, equipo, fecha)
PATCH  /solicitudes/{id}/estado     → actualizar estado
GET    /solicitudes/{id}            → detalle + historial completo

# Agente IA
POST   /agente/procesar-documento   → recibe PDF → OCR → extrae → crea solicitud
POST   /agente/procesar-correo      → recibe payload email → agente decide acción
GET    /agente/buscar-similares     → búsqueda semántica sobre casos anteriores
POST   /agente/verificar-semanal    → trigger manual de verificación semanal de trazabilidad

# Borradores de correo (human-in-the-loop)
GET    /borradores/                 → listar borradores pendientes de aprobación
GET    /borradores/{id}             → detalle del borrador con contexto de la solicitud
PATCH  /borradores/{id}             → editar cuerpo antes de aprobar
POST   /borradores/{id}/aprobar     → aprobar: registra aprobado_por + envía correo
POST   /borradores/{id}/rechazar    → rechazar: registra motivo, no envía

# Notificaciones
GET    /notificaciones/             → historial de notificaciones enviadas
```

---

## Estrategia de desarrollo: TDD + Mock primero

### Regla de oro

**Nunca escribir código de producción antes de un test que falle.** Todo adapter externo (LLM, OCR, email) tiene una implementación `Fake` que se usa en todos los tests. Las implementaciones reales se activan vía `settings.py` y se validan con tests de integración separados.

### Ciclo por módulo

```
1. Escribir test que falla (red)
2. Implementar mínimo para pasar (green)
3. Refactorizar sin romper tests (refactor)
4. Cuando el adapter real esté listo: swap fake → real
5. Test de integración confirma equivalencia del comportamiento
```

### Capas de test

| Capa | Qué prueba | Infra requerida |
|------|------------|-----------------|
| `tests/unit/` | Dominio puro, reglas de negocio, value objects | Ninguna |
| `tests/application/` | Casos de uso con `FakeRepository` en memoria | Ninguna |
| `tests/integration/` | Repositorios Django ORM + pgvector | PostgreSQL Docker |
| `tests/e2e/` | Flujo HTTP completo vía `TestClient` | PostgreSQL Docker |

### Fake adapters estándar

```python
# FakeEmbeddingAdapter — siempre retorna vector fijo
class FakeEmbeddingAdapter(EmbeddingPort):
    def embed(self, text: str) -> list[float]:
        return [0.1] * 768

# FakeLLMAdapter — retorna decisión fija según tipo de input
class FakeLLMAdapter(LLMPort):
    def decide(self, context: str) -> DecisionAgente:
        return DecisionAgente(accion=Accion.CREAR_SOLICITUD, confianza=0.99)

# FakeOCRAdapter — retorna texto hardcodeado
class FakeOCRAdapter(OCRPort):
    def extract_text(self, pdf_path: str) -> str:
        return FAKE_OCR_TEXT  # texto predefinido en tests/fixtures/

# FakeEmailAdapter — guarda en lista en memoria
class FakeEmailAdapter(EmailPort):
    sent: list[dict] = []
    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})
```

---

## Plan de implementación (sprints lineales)

Implementar en este orden estricto. Cada sprint produce código funcional y testeado antes de pasar al siguiente.

### Sprint 1 — Dominio puro + unit tests
- Entidades: `Equipo`, `Garantia`, `SolicitudGarantia`, `ActaEntrega`, `EventoTrazabilidad`, `Proveedor`, `Notificacion`
- Value objects, enums de estado, reglas de negocio
- `tests/unit/` con 100% cobertura del dominio
- Sin DB, sin mocks externos — solo Python puro

### Sprint 2 — Repositorios en memoria + application tests
- Puertos (interfaces ABC) de repositorios para cada módulo
- `FakeRepository` implementando cada puerto
- Casos de uso implementados usando `FakeRepository`
- `tests/application/` completos

### Sprint 3 — Django ORM + integration tests
- Modelos Django por módulo en `infrastructure/`
- Repositorios concretos implementando los puertos
- Migraciones con `manage.py` standalone
- `tests/integration/` contra PostgreSQL (Docker)

### Sprint 4 — FastAPI + e2e tests
- Routers, schemas Pydantic, `config/dependencies.py`
- Dependency injection inyecta repositorios reales en producción, fake en tests
- `tests/e2e/` con `TestClient` de FastAPI

### Sprint 5 — Pipeline agente (100% mockeado)
- `FakeOCRAdapter`, `FakeLLMAdapter`, `FakeEmbeddingAdapter` operativos
- Endpoints `/agente/procesar-documento` y `/agente/procesar-correo` funcionando
- Flujo completo demostrable con datos sintéticos JSON (sin PDFs aún)

### Sprint 6 — Seguimiento, escalamiento y human-in-the-loop
- Módulo `seguimiento`: entidades `BorradorCorreo`, `EventoSeguimiento`
- Caso de uso `VerificarEstadoSemanal`: calcula días sin respuesta por solicitud activa
- Caso de uso `EscalarSolicitud`: genera `BorradorCorreo` cuando se supera el timeout
- Borradores generados por `FakeLLMAdapter` con plantilla realista (datos del equipo, días transcurridos)
- Endpoints `/borradores/` completos: listar, editar, aprobar, rechazar
- Endpoint `/agente/verificar-semanal` funcional
- El `EmailAdapter` solo puede enviar correos en estado `aprobado` — validado en tests
- `tests/application/` para el flujo completo: timeout → borrador → aprobación → envío

### Sprint 7 — Pipeline agente (Gemini real)
- `GeminiEmbeddingAdapter` con text-embedding-004 Matryoshka dim=768
- `GeminiLLMAdapter` para decisiones del agente y generación de borradores con tono formal
- `GeminiOCRAdapter` para extracción de PDFs
- pgvector con chunking 800/100
- Búsqueda semántica `/agente/buscar-similares` funcional

### Sprint 8 — PDFs sintéticos + datos Datecsa completos
- `scripts/generate_fixtures.py` genera 10-15 PDFs con equipos reales Datecsa
- Formato predefinido: encabezado Datecsa, datos equipo, descripción falla, técnico
- Ingesta completa: PDF → OCR → chunks → pgvector
- Demo end-to-end verificable: PDF → solicitud → timeout → borrador → aprobación → correo enviado

---

## Comandos de desarrollo

Todos los comandos del proyecto se ejecutan a través del **Makefile** en la raíz.

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
	docker compose down

migrate:
	uv run python manage.py makemigrations
	uv run python manage.py migrate

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
	uv run mypy src/ api/
```

### Flujo de primera vez

```bash
make install       # instala dependencias con uv + copia .env
make docker-up     # levanta API + PostgreSQL con pgvector
make migrate       # crea tablas en DB
make fixtures      # genera PDFs y JSON sintéticos Datecsa
make test          # corre toda la suite
```

---

## Smoke test del flujo completo

```bash
# 1. Registrar equipo Datecsa
curl -X POST http://localhost:8000/equipos/ \
  -H "Content-Type: application/json" \
  -d '{"serial": "KYO-TASKalfa-2021-001", "marca": "Kyocera", "modelo": "TASKalfa 2553ci", "tipo": "multifuncional_impresion"}'

# 2. Procesar PDF de acta de falla (agente mockeado)
curl -X POST http://localhost:8000/agente/procesar-documento \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "fixtures/pdfs/acta_entrega_kyocera_001.pdf"}'

# 3. Verificar solicitud creada automáticamente
curl http://localhost:8000/solicitudes/

# 4. Ver trazabilidad del equipo
curl http://localhost:8000/equipos/KYO-TASKalfa-2021-001/trazabilidad

# 5. Buscar casos similares (RAG — Sprint 6+)
curl "http://localhost:8000/agente/buscar-similares?q=error+fusor+kyocera"
```

---

## Human-in-the-loop — reglas de negocio

1. **El agente nunca envía correos directamente.** Solo genera `BorradorCorreo` en estado `pendiente_aprobacion`.
2. **Cualquier usuario Datecsa puede aprobar o rechazar** un borrador — no hay un único aprobador fijo. El campo `aprobado_por` registra quién aprobó.
3. **El usuario puede editar el cuerpo** del borrador antes de aprobar (`PATCH /borradores/{id}`). La edición no cambia el estado — sigue en `pendiente_aprobacion`.
4. **Un correo rechazado no se puede reactivar.** Si es rechazado, el agente genera un nuevo borrador en la siguiente verificación (o manualmente).
5. **El timeout es configurable por entorno** (`TIMEOUT_PROVEEDOR_DIAS`, `TIMEOUT_CLIENTE_DIAS`) y aplica igual para proveedores y clientes.
6. **La verificación semanal es idempotente:** si ya existe un borrador `pendiente_aprobacion` para una solicitud, no genera uno nuevo — solo registra el `EventoSeguimiento`.

---

## Convenciones de código

- **Puertos como ABC:** toda interfaz de infraestructura es una clase abstracta en `domain/` o `application/`
- **Casos de uso como clases:** cada caso de uso es una clase con método `execute()`, no funciones sueltas
- **Pydantic para schemas de API:** los modelos de entrada/salida de FastAPI son Pydantic, no las entidades de dominio
- **Django models solo en infrastructure/:** los modelos ORM nunca salen de la capa de infraestructura
- **Settings como singleton:** importar siempre `from config.settings import settings`, nunca `os.environ` directamente
- **Un adapter, una responsabilidad:** `FakeOCRAdapter` solo simula OCR, no parsea ni transforma
