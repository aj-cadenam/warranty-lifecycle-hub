import type { SolicitudGarantia, BorradorCorreo, BuscarResultado, Equipo, VerificarSemanalResult, Notificacion, NuevoEquipoData, ProcesarDocumentoResult, ChatRequest, ChatResponse, HealthResponse, InboxPreview, PipelineResult } from '../types'

const API_BASE = '/api'

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options)
  if (!response.ok) {
    const errorText = await response.text().catch(() => 'Unknown error')
    throw new Error(`HTTP ${response.status}: ${errorText}`)
  }
  return response.json() as Promise<T>
}

export const api = {
  // Solicitudes
  getSolicitudes: (): Promise<SolicitudGarantia[]> =>
    fetchJson<SolicitudGarantia[]>(`${API_BASE}/solicitudes/`),

  getSolicitud: (id: string): Promise<SolicitudGarantia> =>
    fetchJson<SolicitudGarantia>(`${API_BASE}/solicitudes/${id}`),

  crearSolicitud: (data: {
    equipo_id: string
    reportado_por: string
    descripcion_falla: string
  }): Promise<SolicitudGarantia> =>
    fetchJson<SolicitudGarantia>(`${API_BASE}/solicitudes/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  actualizarEstado: (id: string, estado: string): Promise<SolicitudGarantia> =>
    fetchJson<SolicitudGarantia>(`${API_BASE}/solicitudes/${id}/estado`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ estado }),
    }),

  // Borradores
  getBorradores: (): Promise<BorradorCorreo[]> =>
    fetchJson<BorradorCorreo[]>(`${API_BASE}/borradores/`),

  getBorrador: (id: string): Promise<BorradorCorreo> =>
    fetchJson<BorradorCorreo>(`${API_BASE}/borradores/${id}`),

  editarBorrador: (id: string, cuerpo: string): Promise<BorradorCorreo> =>
    fetchJson<BorradorCorreo>(`${API_BASE}/borradores/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cuerpo }),
    }),

  aprobarBorrador: (id: string, aprobadoPor: string): Promise<BorradorCorreo> =>
    fetchJson<BorradorCorreo>(`${API_BASE}/borradores/${id}/aprobar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ aprobado_por: aprobadoPor }),
    }),

  rechazarBorrador: (id: string, motivo: string): Promise<BorradorCorreo> =>
    fetchJson<BorradorCorreo>(`${API_BASE}/borradores/${id}/rechazar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ motivo }),
    }),

  // Equipos
  getEquipos: (): Promise<Equipo[]> =>
    fetchJson<Equipo[]>(`${API_BASE}/equipos/`),

  crearEquipo: (data: NuevoEquipoData): Promise<Equipo> =>
    fetchJson<Equipo>(`${API_BASE}/equipos/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  // Notificaciones
  getNotificaciones: (): Promise<Notificacion[]> =>
    fetchJson<Notificacion[]>(`${API_BASE}/notificaciones/`),

  // Agente
  verificarSemanal: (): Promise<VerificarSemanalResult> =>
    fetchJson<VerificarSemanalResult>(`${API_BASE}/agente/verificar-semanal`, {
      method: 'POST',
    }),

  procesarDocumento: (pdfPath: string): Promise<ProcesarDocumentoResult> =>
    fetchJson<ProcesarDocumentoResult>(`${API_BASE}/agente/procesar-documento`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pdf_path: pdfPath }),
    }),

  uploadDocumento: (file: File): Promise<ProcesarDocumentoResult> => {
    const form = new FormData()
    form.append('file', file)
    return fetchJson<ProcesarDocumentoResult>(`${API_BASE}/agente/procesar-documento/upload`, {
      method: 'POST',
      body: form,
    })
  },

  buscarSimilares: (q: string): Promise<{ resultados: BuscarResultado[] }> =>
    fetchJson<{ resultados: BuscarResultado[] }>(`${API_BASE}/agente/buscar-similares?q=${encodeURIComponent(q)}`),

  chatAgente: (payload: ChatRequest): Promise<ChatResponse> =>
    fetchJson<ChatResponse>(`${API_BASE}/agente/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),

  getHealth: (): Promise<HealthResponse> =>
    fetchJson<HealthResponse>(`${API_BASE}/health`),

  inboxPreview: (): Promise<InboxPreview> =>
    fetchJson<InboxPreview>(`${API_BASE}/agente/inbox-preview`),

  procesarCorreos: (): Promise<PipelineResult> =>
    fetchJson<PipelineResult>(`${API_BASE}/agente/procesar-correos`, { method: 'POST' }),
}
