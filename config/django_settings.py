import dj_database_url
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
    "default": dj_database_url.parse(settings.DATABASE_URL)
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
