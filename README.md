# Datecsa Garantías — Technical Reference

> **Stack:** Python 3.13 · FastAPI · Django ORM (standalone) · PostgreSQL + pgvector · Gemini · React + TypeScript + Vite · Docker

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Map](#module-map)
3. [Data Model & State Machines](#data-model--state-machines)
4. [AI Pipeline](#ai-pipeline)
5. [API Reference](#api-reference)
6. [Frontend Architecture](#frontend-architecture)
7. [Configuration & Dependency Injection](#configuration--dependency-injection)
8. [Observability](#observability)
9. [Testing Strategy](#testing-strategy)
10. [Local Development](#local-development)
11. [Design Decisions](#design-decisions)

---

## Architecture Overview

The system follows **Hexagonal Architecture (Ports & Adapters)** applied per domain module. Each module owns its own `domain → application → infrastructure` stack. Cross-module communication happens exclusively through application-layer use cases — never between infrastructure layers directly.

```
┌─────────────────────────────────────────────────────────┐
│  Primary Adapters (inbound)                             │
│  FastAPI routers · APScheduler · CLI scripts            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  Application Layer (use cases)                          │
│  ProcesarCorreo · OrquestarAcciones · VerificarEstado   │
│  CrearSolicitud · ActualizarEstado · AprobarBorrador    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  Domain Layer (pure Python, zero infra dependencies)    │
│  SolicitudGarantia · BorradorCorreo · EventoTrazab.     │
│  State machines · Business rules · Value objects        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  Secondary Adapters (outbound)                          │
│  Django ORM · pgvector · Gemini LLM/OCR/Embeddings      │
│  Outlook SMTP/IMAP · FakeAdapters (test/dev)            │
└─────────────────────────────────────────────────────────┘
```

**Dependency rule:** domain layer has zero imports from infrastructure. All infrastructure implements abstract ports defined in the domain or application layer.

---

## Module Map

```
src/
├── agente/          # AI orchestration — LLM decisions, email classification, PDF processing
├── equipos/         # Equipment catalog and warranty registry
├── solicitudes/     # Warranty request lifecycle (state machine)
├── seguimiento/     # Draft email management + weekly verification
├── trazabilidad/    # Equipment location tracking (chain of custody)
├── notificaciones/  # Notification dispatch
└── shared/          # BaseEntity, pgvector setup, DB config
```

Each module has the same internal structure:

```
<module>/
├── domain/
│   ├── entities.py      # Rich domain objects with business rules
│   ├── ports.py         # Abstract repository interfaces (ABC)
│   └── value_objects.py
├── application/
│   └── <use_case>.py    # One class per use case, execute() method
└── infrastructure/
    ├── django_models.py # ORM models (never exit this layer)
    └── repositories.py  # Concrete port implementations
```

---

## Data Model & State Machines

### SolicitudGarantia states

```
nueva → validada → despachada → en_reparacion → devuelta → cerrada
                                                          ↘ rechazada
```

State transitions are enforced by the domain entity — invalid transitions raise `ValueError`. The use case `ActualizarEstado` maps inbound transition names to the entity methods (`despachar()`, `iniciar_reparacion()`, `registrar_devolucion()`, `cerrar()`).

### BorradorCorreo states

```
generado → pendiente_aprobacion → aprobado → enviado
                                ↘ rechazado
```

**Invariant:** the email adapter can only send a `BorradorCorreo` in state `aprobado`. This is enforced in `AprobarBorrador.execute()` before calling `EmailPort.send()`. A rejected draft is terminal — the agent generates a new one on the next verification cycle.

### Key entities

| Entity | Key fields | Module |
|--------|-----------|--------|
| `SolicitudGarantia` | `equipo_id`, `garantia_id`, `estado`, `fecha_reporte`, `descripcion_falla` | solicitudes |
| `BorradorCorreo` | `solicitud_id`, `destinatario_tipo`, `asunto`, `cuerpo`, `estado`, `aprobado_por` | seguimiento |
| `EventoTrazabilidad` | `equipo_id`, `solicitud_id`, `ubicacion_anterior`, `ubicacion_nueva`, `metodo_registro` | trazabilidad |
| `EventoSeguimiento` | `solicitud_id`, `tipo_evento`, `dias_sin_respuesta` | seguimiento |

---

## AI Pipeline

### Email classification & processing

```
IMAP inbox (Outlook / Fake)
        │
        ▼
FakeLLMAdapter.classify_email()   or   GeminiLLMAdapter.classify_email()
        │
        ▼  DecisionCorreo
        │  ├── tipo: acta_entrega | actualizacion_proveedor | confirmacion_despacho
        │  │         confirmacion_devolucion | consulta_cliente | otro
        │  ├── equipo_serial
        │  ├── nuevo_estado (optional)
        │  └── informacion_adicional
        │
        ▼
ProcesarCorreo._dispatch()
        ├── acta_entrega       → CrearSolicitud (or ProcesarDocumento if PDF attached)
        ├── actualizacion_*    → ActualizarEstado + EventoTrazabilidad + OrquestarAcciones
        ├── confirmacion_dev.  → ActualizarEstado(devuelta) + OrquestarAcciones (4 drafts)
        ├── consulta_cliente   → EventoSeguimiento + OrquestarAcciones (1 draft)
        └── otro               → ignorado
```

### Weekly verification (human-in-the-loop trigger)

```
VerificarEstadoSemanal.execute()
        │
        ▼  solicitudes in [despachada, en_reparacion]
        │
        ▼  for each solicitud:
        │   dias_sin_respuesta = today - last EventoTrazabilidad
        │   if dias >= TIMEOUT_PROVEEDOR_DIAS → EscalarSolicitud → BorradorCorreo(proveedor)
        │   idempotent: skips if pendiente_aprobacion draft already exists
        │
        ▼  EventoSeguimiento registered regardless
```

### OrquestarAcciones — draft generation

Triggered after any state change. Determines recipients by transition type:

| Transition | Recipients |
|------------|-----------|
| `confirmacion_devolucion` | bodega, despacho, recepción, responsable |
| `actualizacion_proveedor` | responsable |
| `consulta_cliente` | responsable |
| `acta_entrega` | responsable |

Each draft is generated by `LLMPort.generate_email(context)` with a context string containing serial, marca/modelo, solicitud ID, fecha, días sin respuesta. The Gemini adapter produces human-style Spanish prose (warm greeting, specific equipment references, Datecsa signature).

### PDF processing

```
PDF upload → GeminiOCRAdapter.extract_text() → ChunkingService (800/100 overlap)
          → GeminiEmbeddingAdapter.embed() [text-embedding-004, dim=768 Matryoshka]
          → PgVectorStore.upsert()
          → GeminiLLMAdapter.decide() → CREAR_SOLICITUD | ACTUALIZAR_ESTADO | IGNORAR
          → CrearSolicitud.execute()
```

### Semantic search

`GET /agente/buscar-similares?q=...` embeds the query, runs pgvector cosine similarity search, deduplicates by `solicitud_id` from chunk metadata, returns ranked solicitudes.

---

## API Reference

```
# Equipos
GET    /equipos/                     list with filters
POST   /equipos/                     register equipment
GET    /equipos/{id}/garantia        active warranty
GET    /equipos/{id}/trazabilidad    location history

# Solicitudes
POST   /solicitudes/                 create manually
GET    /solicitudes/                 list (filters: estado, equipo, fecha)
PATCH  /solicitudes/{id}/estado      update state
GET    /solicitudes/{id}             detail + full history

# Agente IA
POST   /agente/procesar-documento    PDF → OCR → classify → create solicitud
POST   /agente/procesar-documento/upload   multipart PDF upload
POST   /agente/procesar-correos      IMAP fetch → classify → dispatch (all 10 fake emails)
GET    /agente/inbox-preview         preview unread emails (es_mock: true if IMAP auth fails)
GET    /agente/buscar-similares?q=   semantic search over indexed chunks
POST   /agente/verificar-semanal     manual trigger for weekly timeout check
POST   /agente/ingestar-fixtures     index all PDFs in fixtures/pdfs/ into pgvector
POST   /agente/chat                  agent chat with system context

# Human-in-the-loop
GET    /borradores/                  list pending drafts
GET    /borradores/{id}              draft detail
PATCH  /borradores/{id}              edit body before approving
POST   /borradores/{id}/aprobar      approve → send email
POST   /borradores/{id}/rechazar     reject with motivo

# Support
GET    /notificaciones/              notification history
GET    /trazabilidad/                full location events
```

---

## Frontend Architecture

```
frontend/src/
├── api/client.ts           # Typed fetch wrapper — all API calls in one place
├── types/index.ts          # Shared TypeScript interfaces (mirrors backend schemas)
├── pages/Dashboard.tsx     # Root page — section routing, global toast
├── components/
│   ├── layout/
│   │   ├── LeftPanel.tsx      # Navigation sidebar
│   │   └── CenterPanel.tsx    # Section switcher (dashboard/solicitudes/borradores/…)
│   ├── pipeline/
│   │   └── PipelineRunner.tsx # Animated email pipeline (idle→preview→running→done)
│   ├── agente/
│   │   ├── FloatingAgentButton.tsx
│   │   └── ProcesarDocumentoModal.tsx
│   ├── borradores/BorradorCard.tsx
│   └── solicitudes/SolicitudCard.tsx
└── hooks/
    └── useSolicitudes.ts   # Data fetching hook with polling
```

**State machine in PipelineRunner:** `idle → loading_preview → preview → running → done`. Per-email animation phases: `pending → classifying → processing → orchestrating → done`, cascaded with 1200ms delay between emails. Uses functional `setEmailStates` updater to avoid stale closure bugs, and `Array.from()` (not `Array.fill()`) to avoid shared object references across email cards.

---

## Configuration & Dependency Injection

All configuration lives in `config/settings.py` (Pydantic `BaseSettings`). No `os.environ` calls anywhere else.

```python
# config/dependencies.py — adapter selection at runtime
def get_llm_adapter() -> LLMPort:
    if settings.LLM_PROVIDER == "gemini":
        return GeminiLLMAdapter(api_key=settings.GEMINI_API_KEY)
    return FakeLLMAdapter()
```

The same pattern applies for `get_embedding_adapter()`, `get_ocr_adapter()`, `get_email_reader()`, `get_email_sender()`. FastAPI injects these via `Depends()` — tests override them by providing fake implementations directly.

### Environment variables

```env
# Required
DATABASE_URL=postgresql://user:pass@localhost:5433/garantias

# AI providers ("fake" for dev/test, "gemini" for production)
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini
OCR_BACKEND=gemini
GEMINI_API_KEY=...
EMBEDDING_DIM=768          # Matryoshka — do not change without re-ingesting pgvector

# Email
EMAIL_BACKEND=outlook      # "fake" | "outlook"
EMAIL_ADDRESS=...
EMAIL_PASSWORD=...         # App password (2FA required for Outlook.com)

# Business rules
TIMEOUT_PROVEEDOR_DIAS=7
TIMEOUT_CLIENTE_DIAS=7

# Observability
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
```

**Note on Outlook IMAP:** Microsoft has deprecated basic auth on Outlook.com personal accounts. The adapter wraps `imaplib.IMAP4.error` in `IMAPAuthError`; both `/agente/inbox-preview` and `/agente/procesar-correos` fall back to `FakeEmailReaderAdapter` when auth fails, returning `"es_mock": true` in the preview response. Production deployment would require OAuth2 (Azure app registration).

---

## Observability

All LLM calls are traced via **Langfuse** using the `@observe` decorator on `GeminiLLMAdapter` methods. Each trace captures: input prompt, model response, latency, token counts.

The Langfuse client is initialized lazily — if `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` are absent or invalid, tracing degrades gracefully (the `401 Unauthorized` from the exporter is logged at WARNING, not raised).

---

## Testing Strategy

| Layer | What it tests | Infrastructure |
|-------|--------------|----------------|
| `tests/unit/` | Domain entities, state machines, value objects | None |
| `tests/application/` | Use cases with `FakeRepository` in memory | None |
| `tests/integration/` | Django ORM repositories against real PostgreSQL | Docker |
| `tests/e2e/` | Full HTTP flows via FastAPI `TestClient` | Docker |

**Fake adapters** are first-class citizens in the codebase, not test utilities. They implement the same ports as real adapters and are used in `seed_db.py` regardless of env settings.

```bash
make test              # unit + application (no Docker needed)
make test-integration  # needs Docker
make test-e2e          # needs Docker
```

---

## Local Development

```bash
# First time
make install           # uv sync + copy .env.example
docker compose up -d db
make migrate

# Seed demo data
make seed              # 5 solicitudes + borradores via FakeLLM
make reset             # clears transactional data, preserves equipos/garantias

# Run
make dev               # uvicorn --reload on :8000
cd frontend && npm run dev   # Vite on :5173

# Verify pipeline
curl http://localhost:8000/agente/inbox-preview
curl -X POST http://localhost:8000/agente/procesar-correos
```

---

## Design Decisions

### Why Django ORM without Django server?

Django ORM is the most mature Python ORM with excellent migration tooling and pgvector support. By calling `django.setup()` without `runserver`, we get the full ORM ergonomics (querysets, migrations, admin-compatible models) while FastAPI handles the HTTP layer. The tradeoff is a slightly unusual setup sequence in `config/database.py` — worth it for migration reliability over SQLAlchemy Alembic.

### Why hexagonal per module, not per layer?

A global `domain/` folder creates cross-module coupling and makes it unclear which module "owns" an entity. Per-module hexagonal keeps each bounded context self-contained. The cost is some boilerplate repetition; the benefit is that removing or replacing a module (e.g., swapping `notificaciones` for a different notification system) has zero blast radius on other modules.

### Why FakeAdapters in production code, not only in tests?

Fake adapters are used in `seed_db.py`, the weekly scheduler fallback, and any context where LLM cost/latency is undesirable. Keeping them as first-class implementations (not `unittest.mock` patches) means they stay in sync with the port interface — a port change will break the fake just like it breaks the real adapter, surfacing regressions immediately.

### Why human-in-the-loop for emails?

The agent generates `BorradorCorreo` objects; no email is sent without an explicit `POST /borradores/{id}/aprobar`. This is intentional: LLMs hallucinate, context can be incomplete, and an incorrectly worded email to a provider or client creates real business harm. The approval step is cheap (one click) and catches the long tail of edge cases that unit tests cannot anticipate.

### pgvector Matryoshka embeddings

`text-embedding-004` with `EMBEDDING_DIM=768` uses Matryoshka Representation Learning — embeddings truncated to 768 dimensions retain most of their semantic quality while halving storage vs. the full 3072-dim output. **Do not change `EMBEDDING_DIM` without re-ingesting all chunks** — mixing dimension sizes in the same pgvector index produces undefined similarity scores.

### APScheduler for weekly verification

The scheduler runs `VerificarEstadoSemanal` on a weekly cron. The use case is idempotent: if a `pendiente_aprobacion` draft already exists for a solicitud, it skips draft generation and only writes an `EventoSeguimiento`. Safe to call multiple times or trigger manually via `POST /agente/verificar-semanal`.
