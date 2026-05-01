from django.db import models


class SolicitudGarantiaModel(models.Model):
    equipo_serial = models.CharField(max_length=100)
    garantia_id = models.IntegerField()
    reportado_por = models.CharField(max_length=200)
    descripcion_falla = models.TextField()
    fecha_reporte = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=50, default="nueva")

    class Meta:
        app_label = "solicitudes"
        db_table = "solicitudes_garantia"
