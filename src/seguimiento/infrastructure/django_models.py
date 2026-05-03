from django.db import models


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
    dias_sin_respuesta = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "seguimiento"
        db_table = "borradores_correo"


class EventoSeguimientoModel(models.Model):
    solicitud_id = models.IntegerField()
    tipo_evento = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    dias_sin_respuesta = models.IntegerField(default=0)

    class Meta:
        app_label = "seguimiento"
        db_table = "eventos_seguimiento"
