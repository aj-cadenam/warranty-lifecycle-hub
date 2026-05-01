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
    equipo_serial = models.CharField(max_length=100)
    proveedor = models.ForeignKey(ProveedorModel, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo_cobertura = models.CharField(max_length=200)
    numero_contrato = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=50)

    class Meta:
        app_label = "equipos"
        db_table = "garantias"
