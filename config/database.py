import os
import django
from django.conf import settings as django_conf


def setup_django() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django_settings")
    if not django_conf.configured:
        django.setup()
