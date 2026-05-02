from apscheduler.schedulers.background import BackgroundScheduler

_scheduler = BackgroundScheduler()


def _run_procesar_correos() -> None:
    from config.dependencies import (
        get_llm_adapter, get_email_reader, get_ocr_adapter,
        get_embedding_adapter, get_vector_store,
        get_solicitud_repo, get_garantia_repo, get_trazabilidad_repo,
    )
    from src.agente.application.procesar_correo import ProcesarCorreo
    from src.solicitudes.application.crear_solicitud import CrearSolicitud

    solicitud_repo = get_solicitud_repo()
    caso_uso = ProcesarCorreo(
        llm=get_llm_adapter(),
        email_reader=get_email_reader(),
        ocr=get_ocr_adapter(),
        embedding=get_embedding_adapter(),
        vector_store=get_vector_store(),
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=get_trazabilidad_repo(),
        crear_solicitud=CrearSolicitud(
            solicitud_repo=solicitud_repo,
            garantia_repo=get_garantia_repo(),
        ),
    )
    result = caso_uso.execute()
    if result["procesados"] > 0:
        import logging
        logging.getLogger(__name__).info(
            "procesar_correos: %d procesados", result["procesados"]
        )


def start(interval_minutes: int = 5) -> None:
    _scheduler.add_job(
        _run_procesar_correos,
        trigger="interval",
        minutes=interval_minutes,
        id="procesar_correos",
        replace_existing=True,
    )
    _scheduler.start()


def stop() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
