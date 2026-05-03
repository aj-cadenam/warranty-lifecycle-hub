export type EstadoSolicitud =
  | 'nueva'
  | 'validada'
  | 'despachada'
  | 'en_reparacion'
  | 'devuelta'
  | 'cerrada'

export type EstadoBorrador =
  | 'generado'
  | 'pendiente_aprobacion'
  | 'aprobado'
  | 'enviado'
  | 'rechazado'

export interface Equipo {
  id: string
  serial: string
  nombre: string
  marca: string
  modelo: string
  tipo: string
  ubicacion_fisica: string
  estado: string
}

export interface Garantia {
  id: string
  equipo_id: string
  proveedor_id: string
  fecha_inicio: string
  fecha_fin: string
  tipo_cobertura: string
  estado: string
}

export interface SolicitudGarantia {
  id: string
  equipo_id: string
  garantia_id?: string
  reportado_por: string
  descripcion_falla: string
  estado: EstadoSolicitud
  fecha_reporte: string
  equipo?: Equipo
  eventos?: EventoTrazabilidad[]
}

export interface EventoTrazabilidad {
  id: string
  equipo_id: string
  solicitud_id: string
  ubicacion_anterior: string
  ubicacion_nueva: string
  metodo_registro: string
  timestamp: string
  notas: string
}

export interface BorradorCorreo {
  id: string
  solicitud_id: string
  destinatario_tipo: 'proveedor' | 'cliente' | 'responsable' | 'bodega' | 'despacho' | 'recepcion'
  destinatario_email: string
  asunto: string
  cuerpo: string
  estado: EstadoBorrador
  aprobado_por?: string
  fecha_aprobacion?: string
  motivo_rechazo?: string
  dias_sin_respuesta: number
  created_at?: string
}

export interface VerificarSemanalResult {
  solicitudes_verificadas: number
  borradores_generados: number
  escalaciones: number
  mensaje: string
}

export type NavSection = 'dashboard' | 'garantias' | 'equipos' | 'borradores' | 'verificar' | 'notificaciones'

export interface Notificacion {
  id: string
  tipo: string
  destinatario: string
  canal: string
  estado: string
  timestamp: string
  mensaje?: string
}

export interface BuscarResultado {
  id: string
  equipo_id: string
  descripcion_falla: string
  estado: EstadoSolicitud
  fecha_reporte: string
  similitud: number
}

export interface ProcesarDocumentoResult {
  accion: string
  confianza: number
  razonamiento: string
  solicitud_creada?: SolicitudGarantia
}

export interface NuevoEquipoData {
  serial: string
  nombre: string
  marca: string
  modelo: string
  tipo: string
  ubicacion_fisica: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'agent'
  content: string
  timestamp: Date
}

export interface ChatContexto {
  solicitudes_activas: number
  borradores_pendientes: number
  equipos_activos: string[]
}

export interface ChatRequest {
  mensaje: string
  contexto: ChatContexto
}

export interface ChatResponse {
  respuesta: string
  accion: '' | 'buscar_similares' | 'verificar_semanal'
  query_busqueda: string
}

export interface HealthResponse {
  status: string
  llm_provider: string
}
