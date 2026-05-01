import os
import dj_database_url

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"

INSTALLED_APPS = [
    "src.equipos.infrastructure",
    "src.solicitudes.infrastructure",
    "src.trazabilidad.infrastructure",
    "src.seguimiento.infrastructure",
    "src.notificaciones.infrastructure",
]

_database_url = os.environ.get(
    "DATABASE_URL", "postgresql://user:pass@localhost:5432/garantias"
)
DATABASES = {
    "default": dj_database_url.parse(_database_url)
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
