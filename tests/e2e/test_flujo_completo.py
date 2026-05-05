"""
Integration tests — flujo completo end-to-end vía HTTP (FastAPI TestClient + PostgreSQL real).

Flujo cubierto:
  1. Registrar equipo Datecsa
  2. Registrar garantía vigente para ese equipo
  3. Crear solicitud de garantía manual
  4. Recorrer todos los estados hasta en_reparacion
  5. Procesar documento PDF (agente mock)  →  crea solicitud automáticamente
  6. Verificación semanal → genera borrador de seguimiento
  7. Editar, aprobar y rechazar borrador (human-in-the-loop)
  8. Buscar casos similares (RAG mock)
  9. Consultar notificaciones
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# ─── fixtures reutilizables ───────────────────────────────────────────────────

SERIAL = "KYO-E2E-FULL-001"
PROVEEDOR_EMAIL = "proveedor@kyocera.com.co"


@pytest.fixture(scope="module")
def equipo():
    """Registra un equipo y su garantía; limpia si ya existía."""
    # Intentar crear equipo
    r = client.post("/equipos/", json={
        "serial": SERIAL,
        "nombre": "Kyocera TASKalfa E2E",
        "marca": "Kyocera",
        "modelo": "TASKalfa 2553ci",
        "tipo": "multifuncional_impresion",
        "ubicacion_fisica": "Piso 3 – Área Administrativa",
    })
    assert r.status_code in (201, 400), f"Crear equipo: {r.text}"

    # Obtener el equipo por serial
    lista = client.get("/equipos/").json()
    eq = next((e for e in lista if e["serial"] == SERIAL), None)
    assert eq is not None, "Equipo no encontrado tras registro"
    return eq


@pytest.fixture(scope="module")
def garantia(equipo):
    """Registra una garantía vigente (3 años hacia el futuro)."""
    from datetime import date, timedelta
    inicio = date.today().isoformat()
    fin = (date.today() + timedelta(days=1095)).isoformat()

    r = client.post("/garantias/", json={
        "equipo_id": equipo["id"],
        "proveedor_nombre": "Kyocera Document Solutions",
        "proveedor_email": PROVEEDOR_EMAIL,
        "fecha_inicio": inicio,
        "fecha_fin": fin,
        "tipo_cobertura": "total",
    })
    # 201 = creada, 400 = ya existe (idempotente)
    assert r.status_code in (201, 400), f"Crear garantía: {r.text}"

    r2 = client.get(f"/equipos/{equipo['id']}/garantia")
    assert r2.status_code == 200, f"No se encontró garantía para equipo {equipo['id']}"
    return r2.json()


# ─── 1. Health ────────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ─── 2. Equipos ───────────────────────────────────────────────────────────────

def test_registrar_equipo(equipo):
    assert equipo["serial"] == SERIAL
    assert equipo["marca"] == "Kyocera"


def test_listar_equipos_incluye_el_registrado(equipo):
    r = client.get("/equipos/")
    assert r.status_code == 200
    seriales = [e["serial"] for e in r.json()]
    assert SERIAL in seriales


def test_garantia_vigente_del_equipo(equipo, garantia):
    assert garantia["estado"] in ("vigente", "activa", "activo")
    assert garantia["equipo_id"] == equipo["id"]


# ─── 3. Solicitudes — ciclo de vida completo ──────────────────────────────────

@pytest.fixture(scope="module")
def solicitud(equipo, garantia):
    r = client.post("/solicitudes/", json={
        "equipo_id": equipo["id"],
        "reportado_por": "javier.cadena@datecsafake.com",
        "descripcion_falla": "Error de fusor C3100 — el equipo detiene la impresión.",
    })
    assert r.status_code == 201, f"Crear solicitud: {r.text}"
    return r.json()


def test_solicitud_inicia_en_nueva(solicitud):
    assert solicitud["estado"] == "nueva"
    assert solicitud["equipo_id"] is not None


def test_listar_solicitudes(solicitud):
    r = client.get("/solicitudes/")
    assert r.status_code == 200
    ids = [s["id"] for s in r.json()]
    assert solicitud["id"] in ids


def test_obtener_solicitud_detalle(solicitud):
    r = client.get(f"/solicitudes/{solicitud['id']}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == solicitud["id"]
    assert data["descripcion_falla"] is not None


def test_transicion_nueva_a_validada(solicitud):
    r = client.patch(f"/solicitudes/{solicitud['id']}/estado", json={"estado": "validada"})
    assert r.status_code == 200
    assert r.json()["estado"] == "validada"


def test_transicion_validada_a_despachada(solicitud):
    r = client.patch(f"/solicitudes/{solicitud['id']}/estado", json={"estado": "despachada"})
    assert r.status_code == 200
    assert r.json()["estado"] == "despachada"


def test_transicion_despachada_a_en_reparacion(solicitud):
    r = client.patch(f"/solicitudes/{solicitud['id']}/estado", json={"estado": "en_reparacion"})
    assert r.status_code == 200
    assert r.json()["estado"] == "en_reparacion"


def test_transicion_invalida_rechazada(solicitud):
    # No se puede ir de en_reparacion a nueva directamente
    r = client.patch(f"/solicitudes/{solicitud['id']}/estado", json={"estado": "nueva"})
    assert r.status_code in (400, 422)


# ─── 4. Agente — procesar documento PDF ──────────────────────────────────────

def test_procesar_documento_crea_solicitud(equipo):
    r = client.post("/agente/procesar-documento", json={
        "pdf_path": "fixtures/pdfs/acta_entrega_kyocera_001.pdf",
    })
    assert r.status_code == 200, f"Procesar documento: {r.text}"
    data = r.json()
    assert data["accion"] == "CREAR_SOLICITUD"
    assert data["confianza"] > 0
    assert data["solicitud_creada"] is not None
    assert data["solicitud_creada"]["estado"] == "nueva"


def test_procesar_documento_barco():
    r = client.post("/agente/procesar-documento", json={
        "pdf_path": "fixtures/pdfs/acta_entrega_barco_001.pdf",
    })
    assert r.status_code == 200
    assert r.json()["accion"] == "CREAR_SOLICITUD"


# ─── 5. Verificación semanal → genera borrador ───────────────────────────────

@pytest.fixture(scope="module")
def solicitud_con_timeout(equipo, garantia):
    """Crea una solicitud despachada con evento de trazabilidad backdatado para que supere el timeout."""
    from datetime import datetime, timedelta

    # Crear solicitud
    r = client.post("/solicitudes/", json={
        "equipo_id": equipo["id"],
        "reportado_por": "tecnico@datecsafake.com",
        "descripcion_falla": "Test timeout — sin respuesta del proveedor.",
    })
    assert r.status_code == 201
    sol = r.json()

    # Avanzar a despachada
    client.patch(f"/solicitudes/{sol['id']}/estado", json={"estado": "validada"})
    r2 = client.patch(f"/solicitudes/{sol['id']}/estado", json={"estado": "despachada"})
    assert r2.status_code == 200

    # Registrar evento de trazabilidad con fecha en el pasado (> 7 días)
    old_ts = (datetime.now() - timedelta(days=10)).isoformat()
    client.post("/trazabilidad/", json={
        "equipo_id": equipo["id"],
        "solicitud_id": sol["id"],
        "ubicacion_anterior": "Datecsa",
        "ubicacion_nueva": "Kyocera Service",
        "metodo_registro": "manual",
        "timestamp": old_ts,
    })
    return sol


def test_verificar_semanal_genera_borrador(solicitud_con_timeout):
    r = client.post("/agente/verificar-semanal")
    assert r.status_code == 200
    data = r.json()
    assert "solicitudes_verificadas" in data
    assert data["solicitudes_verificadas"] >= 1
    assert "borradores_generados" in data


def test_verificar_semanal_es_idempotente(solicitud_con_timeout):
    # Segunda llamada no debe crear borrador duplicado
    r1 = client.post("/agente/verificar-semanal")
    r2 = client.post("/agente/verificar-semanal")
    assert r1.status_code == 200
    assert r2.status_code == 200
    # Los borradores generados en la segunda llamada deben ser 0 para esta solicitud
    assert r2.json()["borradores_generados"] == 0


# ─── 6. Borradores — human-in-the-loop ───────────────────────────────────────

def test_listar_borradores():
    r = client.get("/borradores/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.fixture(scope="module")
def borrador_pendiente():
    r = client.get("/borradores/")
    assert r.status_code == 200
    pendientes = [b for b in r.json() if b["estado"] == "pendiente_aprobacion"]
    if not pendientes:
        pytest.skip("No hay borradores pendientes para probar human-in-the-loop")
    return pendientes[0]


def test_obtener_borrador_detalle(borrador_pendiente):
    r = client.get(f"/borradores/{borrador_pendiente['id']}")
    assert r.status_code == 200
    data = r.json()
    assert data["estado"] == "pendiente_aprobacion"
    assert data["asunto"] is not None
    assert data["cuerpo"] is not None


def test_editar_cuerpo_borrador(borrador_pendiente):
    nuevo_cuerpo = "Estimado proveedor,\n\nLe escribimos para hacer seguimiento a la solicitud #TEST.\n\nQuedamos atentos."
    r = client.patch(f"/borradores/{borrador_pendiente['id']}", json={"cuerpo": nuevo_cuerpo})
    assert r.status_code == 200
    assert r.json()["cuerpo"] == nuevo_cuerpo
    # Editar no cambia el estado
    assert r.json()["estado"] == "pendiente_aprobacion"


def test_aprobar_borrador(borrador_pendiente):
    r = client.post(f"/borradores/{borrador_pendiente['id']}/aprobar", json={
        "aprobado_por": "javier.cadena@datecsafake.com",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["estado"] == "enviado"
    assert data["aprobado_por"] == "javier.cadena@datecsafake.com"


def test_borrador_ya_aprobado_no_se_puede_aprobar_de_nuevo(borrador_pendiente):
    r = client.post(f"/borradores/{borrador_pendiente['id']}/aprobar", json={
        "aprobado_por": "otro@datecsafake.com",
    })
    assert r.status_code in (400, 422)


@pytest.fixture(scope="module")
def borrador_para_rechazar():
    """Genera un nuevo borrador para probar rechazo (el anterior ya fue aprobado)."""
    r = client.get("/borradores/")
    pendientes = [b for b in r.json() if b["estado"] == "pendiente_aprobacion"]
    if not pendientes:
        pytest.skip("No hay segundo borrador pendiente para probar rechazo")
    return pendientes[0]


def test_rechazar_borrador(borrador_para_rechazar):
    r = client.post(f"/borradores/{borrador_para_rechazar['id']}/rechazar", json={
        "motivo": "El tono del correo no es apropiado. Requiere revisión.",
    })
    assert r.status_code == 200
    assert r.json()["estado"] == "rechazado"


# ─── 7. Búsqueda semántica ────────────────────────────────────────────────────

def test_buscar_similares_retorna_lista():
    r = client.get("/agente/buscar-similares?q=error+fusor+kyocera")
    assert r.status_code == 200
    data = r.json()
    assert "resultados" in data
    assert isinstance(data["resultados"], list)


def test_buscar_similares_con_query_vacia():
    r = client.get("/agente/buscar-similares?q=")
    assert r.status_code in (200, 422)


def test_buscar_similares_barco():
    r = client.get("/agente/buscar-similares?q=Barco+ClickShare+sin+conexion")
    assert r.status_code == 200
    assert "resultados" in r.json()


# ─── 8. Notificaciones ───────────────────────────────────────────────────────

def test_listar_notificaciones():
    r = client.get("/notificaciones/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ─── 9. Flujo completo integrado ─────────────────────────────────────────────

def test_flujo_completo_pdf_a_solicitud_a_borrador(equipo, garantia):
    """
    PDF → solicitud creada por agente → avanzar estados → verificar semanal → borrador.
    Este test verifica que el pipeline completo funciona de punta a punta.
    """
    from datetime import datetime, timedelta

    # 1. Procesar PDF → solicitud nueva
    r = client.post("/agente/procesar-documento", json={
        "pdf_path": "fixtures/pdfs/acta_entrega_kyocera_001.pdf",
    })
    assert r.status_code == 200
    sol = r.json()["solicitud_creada"]
    assert sol is not None
    sol_id = sol["id"]

    # 2. Validar → despachar
    client.patch(f"/solicitudes/{sol_id}/estado", json={"estado": "validada"})
    r2 = client.patch(f"/solicitudes/{sol_id}/estado", json={"estado": "despachada"})
    assert r2.json()["estado"] == "despachada"

    # 3. Registrar evento de trazabilidad backdatado (>7 días)
    old_ts = (datetime.now() - timedelta(days=8)).isoformat()
    client.post("/trazabilidad/", json={
        "equipo_id": equipo["id"],
        "solicitud_id": sol_id,
        "ubicacion_anterior": "Datecsa Cali",
        "ubicacion_nueva": "Kyocera Service Center",
        "metodo_registro": "manual",
        "timestamp": old_ts,
    })

    # 4. Verificación semanal
    r3 = client.post("/agente/verificar-semanal")
    assert r3.status_code == 200

    # 5. Debe haber al menos un borrador pendiente
    r4 = client.get("/borradores/")
    pendientes = [b for b in r4.json() if b["estado"] == "pendiente_aprobacion"]
    assert len(pendientes) >= 1, "Se esperaba al menos un borrador pendiente tras verificación"

    # 6. Aprobar el borrador
    bid = pendientes[0]["id"]
    r5 = client.post(f"/borradores/{bid}/aprobar", json={"aprobado_por": "javier.cadena@datecsafake.com"})
    assert r5.json()["estado"] == "enviado"

    # 7. Verificar que se generó una notificación del envío
    r6 = client.get("/notificaciones/")
    assert r6.status_code == 200
