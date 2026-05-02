import os
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django_settings")
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5433/garantias")

from config.database import setup_django
setup_django()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    from django.test.utils import setup_test_environment
    setup_test_environment()
