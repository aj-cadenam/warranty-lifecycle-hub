import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

FIXTURES_DIR = Path("fixtures")
PDFS_DIR = FIXTURES_DIR / "pdfs"
PDFS_DIR.mkdir(parents=True, exist_ok=True)

EQUIPOS = [
    {"serial": "KYO-TASKalfa-2021-001", "marca": "Kyocera", "modelo": "TASKalfa 2553ci",
     "tipo": "multifuncional_impresion", "ubicacion": "Piso 3 - Área Administrativa"},
    {"serial": "BAR-CS-2022-014", "marca": "Barco", "modelo": "ClickShare CX-50",
     "tipo": "colaboracion_audiovisual", "ubicacion": "Sala de Juntas Principal"},
    {"serial": "BSP-PMX-2020-007", "marca": "Bose Professional", "modelo": "PowerMatch PM8500N",
     "tipo": "audio_corporativo", "ubicacion": "Auditorio"},
    {"serial": "CRE-TSW-2023-003", "marca": "Crestron", "modelo": "TSW-770",
     "tipo": "automatizacion_sala", "ubicacion": "Sala Ejecutiva B"},
    {"serial": "LG-MRI-2022-021", "marca": "LG Business", "modelo": "55SM5KE",
     "tipo": "senalizacion_digital", "ubicacion": "Recepción Principal"},
]

FALLAS = [
    ("KYO-TASKalfa-2021-001", "Carlos Ramírez", "soporte@kyocera.co",
     "Error de fusor C3100. El equipo muestra código C3100 y detiene impresión a los 5 minutos.",
     "Afecta área administrativa con 40+ usuarios. Urgente para operación diaria."),
    ("BAR-CS-2022-014", "Ana Gómez", "soporte@barco.com",
     "Botón ClickShare no establece conexión con pantalla principal. WiFi conectado, sin video.",
     "Sala de juntas inutilizable. Afecta reuniones ejecutivas diarias."),
    ("BSP-PMX-2020-007", "Luis Torres", "soporte@bose.com",
     "Canales 3 y 4 del amplificador sin señal de salida. Canales 1, 2, 5-8 funcionan.",
     "Detectado durante evento corporativo con 200 asistentes. Sistema de audio crítico."),
    ("CRE-TSW-2023-003", "María Castro", "soporte@crestron.com",
     "Panel táctil TSW-770 no responde al toque. Pantalla enciende pero no registra input.",
     "Sala ejecutiva sin control de luces, cortinas y videoconferencia."),
    ("LG-MRI-2022-021", "Pedro Silva", "soporte@lg.com",
     "Monitor industrial con banda horizontal de píxeles muertos a 30cm del borde superior.",
     "Señalización digital de recepción afectada. Impacto en imagen corporativa."),
]


def generar_acta_pdf(serial: str, tecnico: str, proveedor_email: str, falla: str, situacion: str) -> str:
    equipo = next(e for e in EQUIPOS if e["serial"] == serial)
    filename = PDFS_DIR / f"acta_entrega_{serial.replace('-', '_').lower()}.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>DATECSA S.A.</b>", styles["Title"]))
    story.append(Paragraph("ACTA DE ENTREGA — GARANTÍA DE EQUIPO", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("<b>Fecha:</b> 2026-04-30", styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("<b>DATOS DEL EQUIPO</b>", styles["Heading3"]))
    story.append(Paragraph(f"Serial: {serial}", styles["Normal"]))
    story.append(Paragraph(f"Marca: {equipo['marca']}", styles["Normal"]))
    story.append(Paragraph(f"Modelo: {equipo['modelo']}", styles["Normal"]))
    story.append(Paragraph(f"Tipo: {equipo['tipo']}", styles["Normal"]))
    story.append(Paragraph(f"Ubicación: {equipo['ubicacion']}", styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("<b>DESCRIPCIÓN DE LA FALLA</b>", styles["Heading3"]))
    story.append(Paragraph(falla, styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("<b>SITUACIÓN Y CONTEXTO</b>", styles["Heading3"]))
    story.append(Paragraph(situacion, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"<b>Técnico responsable:</b> {tecnico}", styles["Normal"]))
    story.append(Paragraph(f"<b>Proveedor destino:</b> {proveedor_email}", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Firma técnico: ____________________", styles["Normal"]))
    story.append(Paragraph("Firma recepción: ____________________", styles["Normal"]))

    doc.build(story)
    print(f"  ✓ {filename}")
    return str(filename)


def main():
    print("Generando fixtures JSON...")
    (FIXTURES_DIR / "equipos.json").write_text(json.dumps(EQUIPOS, indent=2, ensure_ascii=False))

    proveedores = [
        {"nombre": "Kyocera Document Solutions", "email": "soporte@kyocera.co", "tiempo_respuesta_dias": 5},
        {"nombre": "Barco NV Colombia", "email": "soporte@barco.com", "tiempo_respuesta_dias": 7},
        {"nombre": "Bose Professional", "email": "soporte@bose.com", "tiempo_respuesta_dias": 10},
        {"nombre": "Crestron Electronics", "email": "soporte@crestron.com", "tiempo_respuesta_dias": 7},
        {"nombre": "LG Business Solutions", "email": "soporte@lg.com", "tiempo_respuesta_dias": 5},
    ]
    (FIXTURES_DIR / "proveedores.json").write_text(json.dumps(proveedores, indent=2, ensure_ascii=False))

    print("Generando PDFs sintéticos...")
    for serial, tecnico, email, falla, situacion in FALLAS:
        generar_acta_pdf(serial, tecnico, email, falla, situacion)

    print("Done. Fixtures generados en fixtures/")


if __name__ == "__main__":
    main()
