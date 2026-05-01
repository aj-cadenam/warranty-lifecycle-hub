from config.settings import settings


def test_settings_carga_con_defaults():
    assert settings.LLM_PROVIDER == "fake"
    assert settings.EMBEDDING_PROVIDER == "fake"
    assert settings.TIMEOUT_PROVEEDOR_DIAS == 7
    assert settings.TIMEOUT_CLIENTE_DIAS == 7
    assert settings.EMBEDDING_DIM == 768
    assert settings.OCR_BACKEND == "mock"
    assert settings.EMAIL_BACKEND == "mock"


def test_database_url_tiene_formato_postgresql():
    assert settings.DATABASE_URL.startswith("postgresql://")
