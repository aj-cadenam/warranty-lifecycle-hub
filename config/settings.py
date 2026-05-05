from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/garantias"

    LLM_PROVIDER: str = "fake"
    GEMINI_API_KEY: str = ""

    EMBEDDING_PROVIDER: str = "fake"
    EMBEDDING_DIM: int = 768

    OCR_BACKEND: str = "mock"
    EMAIL_BACKEND: str = "mock"        # "mock" | "outlook"
    EMAIL_ADDRESS: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_IMAP_FOLDER: str = "INBOX"
    EMAIL_POLLING_INTERVAL_MINUTES: int = 5

    # Internal contacts — set these in .env for production
    RESPONSABLE_GARANTIAS_EMAIL: str = "responsable@datecsafake.com"
    BODEGA_EMAIL: str = "bodega@datecsafake.com"
    DESPACHO_EMAIL: str = "despacho@datecsafake.com"
    RECEPCION_EMAIL: str = "recepcion@datecsafake.com"

    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""

    TIMEOUT_PROVEEDOR_DIAS: int = 7
    TIMEOUT_CLIENTE_DIAS: int = 7

    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret"
    DJANGO_SETTINGS_MODULE: str = "config.django_settings"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
