"""Limpia la BD y carga datos de demostración:
- 5 solicitudes con distintos estados y antigüedad
- Eventos de trazabilidad para las que llevan >7 días con el proveedor
- Borradores de seguimiento generados vía VerificarEstadoSemanal (LLM fake)

Uso:
    uv run python scripts/seed_db.py
"""
import django
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django_settings")
django.setup()

from datetime import datetime, timedelta, date
from src.seguimiento.infrastructure.django_models import BorradorCorreoModel, EventoSeguimientoModel
from src.trazabilidad.infrastructure.django_models import EventoTrazabilidadModel
from src.solicitudes.infrastructure.django_models import SolicitudGarantiaModel
from src.equipos.infrastructure.django_models import GarantiaModel

# ── Limpiar datos transaccionales ────────────────────────────────────────────
BorradorCorreoModel.objects.all().delete()
EventoSeguimientoModel.objects.all().delete()
EventoTrazabilidadModel.objects.all().delete()
SolicitudGarantiaModel.objects.all().delete()
print("✓ Datos anteriores eliminados")

# ── Mapear serial → garantia_id ──────────────────────────────────────────────
garantias = {g.equipo_serial: g.id for g in GarantiaModel.objects.all()}

SOLICITUDES = [
    # (serial, estado, falla, días_atrás)
    (
        "KYO-TASKalfa-2021-001",
        "despachada",
        "Error fusor C3100 — falla en calentamiento al inicio del día",
        22,
    ),
    (
        "BAR-CS-2022-014",
        "en_reparacion",
        "Pantalla táctil sin respuesta, botón de encendido intermitente",
        15,
    ),
    (
        "BSP-PMX-2020-007",
        "despachada",
        "Distorsión de audio en canal derecho, ruido en frecuencias bajas",
        10,
    ),
    (
        "CRE-TSW-2023-003",
        "nueva",
        "Pantalla táctil no responde después de actualización de firmware",
        3,
    ),
    (
        "LG-MRI-2022-021",
        "validada",
        "Imagen con franjas verticales en la zona inferior de la pantalla",
        2,
    ),
]

solicitudes_creadas = []
for serial, estado, falla, dias_atras in SOLICITUDES:
    garantia_id = garantias.get(serial)
    if not garantia_id:
        print(f"  ⚠ Sin garantía para {serial} — omitido")
        continue

    fecha = date.today() - timedelta(days=dias_atras)
    s = SolicitudGarantiaModel(
        equipo_serial=serial,
        garantia_id=garantia_id,
        reportado_por="Javier Cadena",
        descripcion_falla=falla,
        estado=estado,
    )
    s.fecha_reporte = fecha
    s.save()
    solicitudes_creadas.append((s, serial, estado, dias_atras))

    # Trazabilidad sólo para casos activos con más de 7 días
    if dias_atras > 7 and estado in ("despachada", "en_reparacion"):
        EventoTrazabilidadModel.objects.create(
            solicitud_id=s.id,
            equipo_id=serial,
            ubicacion_anterior="Sede Datecsa",
            ubicacion_nueva="Proveedor",
            metodo_registro="manual",
            timestamp=datetime.now() - timedelta(days=dias_atras),
        )

print(f"✓ {len(solicitudes_creadas)} solicitudes creadas")
for s, serial, estado, dias in solicitudes_creadas:
    marca = "·" if dias <= 7 else ("⏰" if dias <= 14 else "🔴")
    print(f"  {marca} [{s.id}] {serial} — {estado} — {dias}d atrás")

# ── Generar borradores con VerificarEstadoSemanal (siempre usa LLM fake) ─────
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter
from src.seguimiento.infrastructure.repositories import (
    DjangoBorradorCorreoRepository,
    DjangoEventoSeguimientoRepository,
)
from src.solicitudes.infrastructure.repositories import DjangoSolicitudRepository
from src.trazabilidad.infrastructure.repositories import DjangoTrazabilidadRepository
from src.seguimiento.application.verificar_estado_semanal import VerificarEstadoSemanal

resultado = VerificarEstadoSemanal(
    solicitud_repo=DjangoSolicitudRepository(),
    trazabilidad_repo=DjangoTrazabilidadRepository(),
    borrador_repo=DjangoBorradorCorreoRepository(),
    seguimiento_repo=DjangoEventoSeguimientoRepository(),
    llm=FakeLLMAdapter(),
    timeout_proveedor_dias=7,
    timeout_cliente_dias=7,
).execute()

print(
    f"✓ Verificación semanal: {resultado['solicitudes_verificadas']} revisadas, "
    f"{resultado['borradores_generados']} borradores generados"
)
print("\n¡Listo! Base de datos populada para demostración.")
