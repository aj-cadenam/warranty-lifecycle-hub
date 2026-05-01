from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/garantias"

    LLM_PROVIDER: str = "fake"
    GEMINI_API_KEY: str = ""

    EMBEDDING_PROVIDER: str = "fake"
    EMBEDDING_DIM: int = 768

    OCR_BACKEND: str = "mock"
    EMAIL_BACKEND: str = "mock"
    EMAIL_HOST: str = ""

    TIMEOUT_PROVEEDOR_DIAS: int = 7
    TIMEOUT_CLIENTE_DIAS: int = 7

    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret"
    DJANGO_SETTINGS_MODULE: str = "config.django_settings"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
