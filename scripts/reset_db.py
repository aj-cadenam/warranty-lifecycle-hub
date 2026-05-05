"""Borra todos los datos transaccionales (solicitudes, borradores, trazabilidad, seguimiento).
Equipos y garantías se conservan.
"""
import django
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django_settings")
django.setup()

from src.seguimiento.infrastructure.django_models import BorradorCorreoModel, EventoSeguimientoModel
from src.trazabilidad.infrastructure.django_models import EventoTrazabilidadModel
from src.solicitudes.infrastructure.django_models import SolicitudGarantiaModel

counts = {
    "borradores": BorradorCorreoModel.objects.count(),
    "eventos_seguimiento": EventoSeguimientoModel.objects.count(),
    "trazabilidad": EventoTrazabilidadModel.objects.count(),
    "solicitudes": SolicitudGarantiaModel.objects.count(),
}

BorradorCorreoModel.objects.all().delete()
EventoSeguimientoModel.objects.all().delete()
EventoTrazabilidadModel.objects.all().delete()
SolicitudGarantiaModel.objects.all().delete()

print("✓ Base de datos limpia")
for tabla, n in counts.items():
    print(f"  {tabla}: {n} registros eliminados")
