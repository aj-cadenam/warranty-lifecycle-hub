from django.db import models


class EventoTrazabilidadModel(models.Model):
    equipo_id = models.CharField(max_length=100)
    solicitud_id = models.IntegerField()
    ubicacion_anterior = models.CharField(max_length=200)
    ubicacion_nueva = models.CharField(max_length=200)
    responsable = models.CharField(max_length=200)
    timestamp = models.DateTimeField()
    metodo_registro = models.CharField(max_length=50, default="manual")

    class Meta:
        app_label = "trazabilidad"
        db_table = "eventos_trazabilidad"
