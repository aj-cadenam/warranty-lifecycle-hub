from django.db import models


class NotificacionModel(models.Model):
    destinatario = models.EmailField()
    tipo = models.CharField(max_length=100)
    canal = models.CharField(max_length=50, default="email")
    estado = models.CharField(max_length=50, default="enviada")
    timestamp = models.DateTimeField(auto_now_add=True)
    contenido = models.TextField(blank=True)

    class Meta:
        app_label = "notificaciones"
        db_table = "notificaciones"
