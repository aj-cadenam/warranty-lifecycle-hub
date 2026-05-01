from src.agente.application.procesar_documento import ProcesarDocumento
from src.agente.infrastructure.ocr.fake_ocr_adapter import FakeOCRAdapter
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter
from src.agente.infrastructure.embeddings.fake_embedding_adapter import FakeEmbeddingAdapter
from src.solicitudes.application.crear_solicitud import CrearSolicitud
from tests.application.fakes import FakeSolicitudRepository, FakeGarantiaRepository, FakeEquipoRepository
from src.equipos.domain.entities import Equipo, Garantia, TipoEquipo
from datetime import date, timedelta


def _setup_equipo_con_garantia():
    equipo_repo = FakeEquipoRepository()
    garantia_repo = FakeGarantiaRepository()
    equipo = Equipo(serial="KYO-TASKalfa-2021-001", nombre="Kyocera", marca="Kyocera",
                    modelo="TASKalfa", tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION, ubicacion_fisica="Piso 3")
    equipo_repo.save(equipo)
    garantia = Garantia(equipo_id="KYO-TASKalfa-2021-001", proveedor_id="prov-1",
                        fecha_inicio=date.today() - timedelta(days=30),
                        fecha_fin=date.today() + timedelta(days=335), tipo_cobertura="Total")
    garantia_repo.save(garantia)
    return equipo_repo, garantia_repo


def test_procesar_documento_crea_solicitud():
    equipo_repo, garantia_repo = _setup_equipo_con_garantia()
    solicitud_repo = FakeSolicitudRepository()

    caso_uso = ProcesarDocumento(
        ocr=FakeOCRAdapter(),
        llm=FakeLLMAdapter(),
        embedding=FakeEmbeddingAdapter(),
        crear_solicitud=CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo),
    )

    resultado = caso_uso.execute(pdf_path="fixtures/pdfs/acta_entrega_kyocera_001.pdf")

    assert resultado.accion == "crear_solicitud"
    solicitudes = solicitud_repo.find_all()
    assert len(solicitudes) == 1
    assert "C3100" in solicitudes[0].descripcion_falla
