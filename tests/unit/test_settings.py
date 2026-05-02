from config.settings import settings


def test_settings_carga_con_defaults():
    assert settings.LLM_PROVIDER in ("fake", "gemini")
    assert settings.EMBEDDING_PROVIDER in ("fake", "gemini")
    assert settings.TIMEOUT_PROVEEDOR_DIAS == 7
    assert settings.TIMEOUT_CLIENTE_DIAS == 7
    assert settings.EMBEDDING_DIM == 768
    assert settings.OCR_BACKEND in ("mock", "gemini")
    assert settings.EMAIL_BACKEND in ("mock", "outlook")


def test_database_url_tiene_formato_postgresql():
    assert settings.DATABASE_URL.startswith("postgresql://")
