import { useState, useEffect } from 'react'
import { Plus, Search, Shield, Monitor, Inbox, FileText, Bell, ChevronRight } from 'lucide-react'
import type { NavSection, SolicitudGarantia, BorradorCorreo, Equipo, Notificacion } from '../../types'
import { SolicitudCard } from '../solicitudes/SolicitudCard'
import { BorradorCard } from '../borradores/BorradorCard'
import { SolicitudCardSkeleton } from '../ui/Skeleton'
import { api } from '../../api/client'
import { NewSolicitudModal } from './NewSolicitudModal'
import { NuevoEquipoModal } from '../equipos/NuevoEquipoModal'
import { ProcesarDocumentoModal } from '../agente/ProcesarDocumentoModal'
import { PipelineRunner } from '../pipeline/PipelineRunner'

const SECTION_TITLES: Record<NavSection, string> = {
  dashboard:      'Inicio',
  garantias:      'Casos activos',
  equipos:        'Equipos registrados',
  borradores:     'Correos para aprobar',
  verificar:      'Revisión semanal',
  notificaciones: 'Notificaciones',
}

interface CenterPanelProps {
  activeSection: NavSection
  onSectionChange: (section: NavSection) => void
  solicitudes: SolicitudGarantia[]
  borradores: BorradorCorreo[]
  equipos: Equipo[]
  notificaciones: Notificacion[]
  isLoadingSolicitudes: boolean
  isLoadingBorradores: boolean
  isLoadingEquipos: boolean
  isLoadingNotificaciones: boolean
  onToast: (message: string, type?: 'success' | 'error' | 'info') => void
}

export function CenterPanel({
  activeSection,
  onSectionChange,
  solicitudes,
  borradores,
  equipos,
  notificaciones,
  isLoadingSolicitudes,
  isLoadingBorradores,
  isLoadingEquipos,
  isLoadingNotificaciones,
  onToast,
}: CenterPanelProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [showNewSolicitudModal, setShowNewSolicitudModal] = useState(false)
  const [showNuevoEquipoModal, setShowNuevoEquipoModal] = useState(false)
  const [showProcesarDocumentoModal, setShowProcesarDocumentoModal] = useState(false)
  const [llmProvider, setLlmProvider] = useState('...')

  useEffect(() => {
    api.getHealth().then(h => setLlmProvider(h.llm_provider)).catch(() => setLlmProvider('?'))
  }, [])

  const title = SECTION_TITLES[activeSection]

  const filteredSolicitudes = solicitudes.filter((s) => {
    if (!searchQuery) return true
    const q = searchQuery.toLowerCase()
    return (
      s.id.toLowerCase().includes(q) ||
      s.equipo_id.toLowerCase().includes(q) ||
      s.descripcion_falla?.toLowerCase().includes(q) ||
      s.estado.toLowerCase().includes(q) ||
      s.reportado_por?.toLowerCase().includes(q) ||
      s.equipo?.serial?.toLowerCase().includes(q) ||
      s.equipo?.marca?.toLowerCase().includes(q) ||
      s.equipo?.modelo?.toLowerCase().includes(q)
    )
  })

  const filteredBorradores = borradores.filter((b) => {
    if (!searchQuery) return true
    const q = searchQuery.toLowerCase()
    return (
      b.id.toLowerCase().includes(q) ||
      b.asunto?.toLowerCase().includes(q) ||
      b.destinatario_email?.toLowerCase().includes(q) ||
      b.solicitud_id?.toLowerCase().includes(q)
    )
  })

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#f5f5f5]">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-800">{title}</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              {activeSection === 'garantias' && `${solicitudes.filter(s => s.estado !== 'cerrada').length} casos activos`}
              {activeSection === 'borradores' && (() => {
                const pendientes = borradores.filter(b => b.estado === 'pendiente_aprobacion').length
                return pendientes > 0 ? `${pendientes} correos esperando tu revisión` : 'Sin correos pendientes'
              })()}
              {activeSection === 'equipos' && `${equipos.length} equipos registrados`}
              {activeSection === 'dashboard' && 'Procesa correos y gestiona el flujo completo del pipeline'}
              {activeSection === 'verificar' && (() => {
                const activas = solicitudes.filter(s => s.estado !== 'cerrada').length
                const pendientes = borradores.filter(b => b.estado === 'pendiente_aprobacion').length
                return `${activas} casos activos${pendientes > 0 ? ` · ${pendientes} correos pendientes` : ''}`
              })()}
              {activeSection === 'notificaciones' && `${notificaciones.length} notificaciones`}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {(activeSection === 'dashboard' || activeSection === 'garantias') && (
              <button
                onClick={() => setShowProcesarDocumentoModal(true)}
                className="flex items-center gap-1.5 px-3 py-2 border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors"
              >
                <FileText size={14} />
                Procesar PDF
              </button>
            )}
            {activeSection === 'equipos' ? (
              <button
                onClick={() => setShowNuevoEquipoModal(true)}
                className="flex items-center gap-1.5 px-3 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors"
              >
                <Plus size={14} />
                Nuevo Equipo
              </button>
            ) : (
              <button
                onClick={() => setShowNewSolicitudModal(true)}
                className="flex items-center gap-1.5 px-3 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors"
              >
                <Plus size={14} />
                Nueva Solicitud
              </button>
            )}
          </div>
        </div>

        {/* Filter search for garantias / borradores */}
        {(activeSection === 'garantias' || activeSection === 'borradores') && (
          <div className="mt-3 relative">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={
                activeSection === 'borradores'
                  ? 'Buscar por destinatario, asunto...'
                  : 'Buscar por serial, falla, estado...'
              }
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-colors"
            />
          </div>
        )}
      </div>

      {/* Content area */}
      <div className="flex-1 overflow-y-auto px-6 py-4">

          {/* DASHBOARD — Pipeline Runner */}
          {activeSection === 'dashboard' && (
            <PipelineRunner
              solicitudes={solicitudes}
              onNavigateToBorradores={() => onSectionChange('borradores')}
              onToast={onToast}
            />
          )}

          {/* GARANTIAS */}
          {activeSection === 'garantias' && (
            <div>
              {isLoadingSolicitudes ? (
                <div className="space-y-3">
                  {[1, 2, 3, 4].map((i) => <SolicitudCardSkeleton key={i} />)}
                </div>
              ) : filteredSolicitudes.length === 0 ? (
                <EmptyState
                  icon={Shield}
                  title={searchQuery ? 'Sin resultados' : 'Sin solicitudes'}
                  description={
                    searchQuery
                      ? `No se encontraron solicitudes para "${searchQuery}"`
                      : 'No hay solicitudes de garantía registradas.'
                  }
                />
              ) : (
                <div className="space-y-3">
                  {filteredSolicitudes.map((s) => (
                    <SolicitudCard key={s.id} solicitud={s} />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* EQUIPOS */}
          {activeSection === 'equipos' && (
            <div>
              {isLoadingEquipos ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => <SolicitudCardSkeleton key={i} />)}
                </div>
              ) : equipos.length === 0 ? (
                <EmptyState
                  icon={Monitor}
                  title="Sin equipos"
                  description="No hay equipos registrados en el sistema."
                />
              ) : (
                <div className="space-y-3">
                  {equipos.map((equipo) => (
                    <EquipoCard key={equipo.id} equipo={equipo} />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* BORRADORES */}
          {activeSection === 'borradores' && (
            <div>
              {isLoadingBorradores ? (
                <div className="space-y-3">
                  {[1, 2].map((i) => <SolicitudCardSkeleton key={i} />)}
                </div>
              ) : filteredBorradores.length === 0 ? (
                <EmptyState
                  icon={Inbox}
                  title={searchQuery ? 'Sin resultados' : 'Sin borradores'}
                  description={
                    searchQuery
                      ? `No se encontraron borradores para "${searchQuery}"`
                      : 'No hay borradores pendientes de aprobación.'
                  }
                />
              ) : (
                <div className="space-y-4">
                  {filteredBorradores.map((b) => (
                    <BorradorCard
                      key={b.id}
                      borrador={b}
                      onActionSuccess={(message, type) => onToast(message, type)}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* NOTIFICACIONES */}
          {activeSection === 'notificaciones' && (
            <div>
              {isLoadingNotificaciones ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => <SolicitudCardSkeleton key={i} />)}
                </div>
              ) : notificaciones.length === 0 ? (
                <EmptyState
                  icon={Bell}
                  title="Sin notificaciones"
                  description="No hay notificaciones registradas en el sistema."
                />
              ) : (
                <div className="space-y-3">
                  {notificaciones.map((n) => (
                    <NotificacionCard key={n.id} notificacion={n} />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* VERIFICAR — KPIs + lista de urgencia */}
          {activeSection === 'verificar' && (
            <div className="space-y-5">
              <div className="grid grid-cols-3 gap-3">
                <ActionKPI
                  label="Requieren acción"
                  value={solicitudes.filter(s => s.estado === 'nueva' || s.estado === 'validada').length}
                  subLabel="nuevas y validadas"
                  color="amber"
                  icon="⚡"
                />
                <ActionKPI
                  label="Con el proveedor"
                  value={solicitudes.filter(s => s.estado === 'despachada' || s.estado === 'en_reparacion').length}
                  subLabel="despachadas · en reparación"
                  color="purple"
                  icon="🔧"
                />
                <ActionKPI
                  label="Correos por aprobar"
                  value={borradores.filter(b => b.estado === 'pendiente_aprobacion').length}
                  subLabel="esperando tu revisión"
                  color={borradores.filter(b => b.estado === 'pendiente_aprobacion').length > 0 ? 'red' : 'slate'}
                  icon="✉️"
                />
              </div>
              {isLoadingSolicitudes ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => <SolicitudCardSkeleton key={i} />)}
                </div>
              ) : solicitudes.length === 0 ? (
                <EmptyState
                  icon={Shield}
                  title="Sin casos activos"
                  description="No hay solicitudes registradas. Procesa un PDF o crea una manualmente."
                />
              ) : (
                <UrgencyGroups solicitudes={solicitudes} onVerTodos={() => onSectionChange('garantias')} />
              )}
            </div>
          )}
        </div>

      {/* Modals */}
      {showNewSolicitudModal && (
        <NewSolicitudModal
          equipos={equipos}
          onClose={() => setShowNewSolicitudModal(false)}
          onSuccess={(message) => {
            onToast(message, 'success')
            setShowNewSolicitudModal(false)
          }}
          onError={(message) => onToast(message, 'error')}
        />
      )}

      {showNuevoEquipoModal && (
        <NuevoEquipoModal
          onClose={() => setShowNuevoEquipoModal(false)}
          onSuccess={(message) => {
            onToast(message, 'success')
            setShowNuevoEquipoModal(false)
          }}
          onError={(message) => onToast(message, 'error')}
        />
      )}

      {showProcesarDocumentoModal && (
        <ProcesarDocumentoModal
          onClose={() => setShowProcesarDocumentoModal(false)}
          onSuccess={(message) => onToast(message, 'success')}
          onError={(message) => onToast(message, 'error')}
        />
      )}
    </div>
  )
}

// ── Helper components ──────────────────────────────────────────────────────────

interface ActionKPIProps {
  label: string
  value: number
  subLabel: string
  color: 'amber' | 'purple' | 'red' | 'green' | 'slate'
  icon: string
}

function ActionKPI({ label, value, subLabel, color, icon }: ActionKPIProps) {
  const colors = {
    amber:  { bg: 'bg-amber-50',  border: 'border-amber-200',  num: 'text-amber-600',  bar: 'bg-amber-400' },
    purple: { bg: 'bg-purple-50', border: 'border-purple-200', num: 'text-purple-600', bar: 'bg-purple-400' },
    red:    { bg: 'bg-red-50',    border: 'border-red-200',    num: 'text-red-600',    bar: 'bg-red-400' },
    green:  { bg: 'bg-green-50',  border: 'border-green-200',  num: 'text-green-600',  bar: 'bg-green-400' },
    slate:  { bg: 'bg-slate-50',  border: 'border-slate-200',  num: 'text-slate-500',  bar: 'bg-slate-300' },
  }
  const c = colors[color]
  return (
    <div className={`rounded-lg border ${c.border} ${c.bg} p-3 relative overflow-hidden`}>
      <div className={`absolute top-0 left-0 w-1 h-full ${c.bar}`} />
      <p className="text-xs text-slate-500 mb-1 pl-2">{label}</p>
      <p className={`text-2xl font-bold pl-2 ${c.num}`}>{value}</p>
      <p className="text-xs text-slate-400 mt-0.5 pl-2">{subLabel}</p>
    </div>
  )
}

function getDays(fecha: string) {
  const normalized = fecha.includes('T') ? fecha : `${fecha}T00:00`
  return Math.max(0, Math.floor((Date.now() - new Date(normalized).getTime()) / 86400000))
}

function UrgencyGroups({ solicitudes, onVerTodos }: { solicitudes: import('../../types').SolicitudGarantia[]; onVerTodos: () => void }) {
  const DASHBOARD_LIMIT = 5
  const activas = solicitudes.filter(s => s.estado !== 'cerrada')
  const urgentes = activas.filter(s => getDays(s.fecha_reporte) > 14).sort((a, b) => getDays(b.fecha_reporte) - getDays(a.fecha_reporte))
  const atencion = activas.filter(s => getDays(s.fecha_reporte) > 7 && getDays(s.fecha_reporte) <= 14)
  const normales = activas.filter(s => getDays(s.fecha_reporte) <= 7)

  // Merge all activas sorted by urgency, limit to DASHBOARD_LIMIT
  const sorted = [...urgentes, ...atencion, ...normales]
  const visible = sorted.slice(0, DASHBOARD_LIMIT)
  const remaining = sorted.length - visible.length

  const Group = ({ title, dot, items }: { title: string; dot: string; items: typeof activas }) => {
    if (items.length === 0) return null
    return (
      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className={`w-2 h-2 rounded-full ${dot}`} />
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">{title}</h3>
          <span className="text-xs text-slate-400">({items.length})</span>
        </div>
        <div className="space-y-2">
          {items.map(s => <SolicitudCard key={s.id} solicitud={s} />)}
        </div>
      </div>
    )
  }

  const urgentesVisible = visible.filter(s => getDays(s.fecha_reporte) > 14)
  const atencionVisible = visible.filter(s => getDays(s.fecha_reporte) > 7 && getDays(s.fecha_reporte) <= 14)
  const normalesVisible = visible.filter(s => getDays(s.fecha_reporte) <= 7)

  return (
    <div className="space-y-5">
      <Group title="Urgente · +14 días" dot="bg-red-400" items={urgentesVisible} />
      <Group title="Atención · 7-14 días" dot="bg-amber-400" items={atencionVisible} />
      <Group title="Al día · <7 días" dot="bg-green-400" items={normalesVisible} />
      {remaining > 0 && (
        <button
          onClick={onVerTodos}
          className="w-full flex items-center justify-center gap-1.5 py-2.5 text-sm text-brand-600 hover:text-brand-700 hover:bg-brand-50 rounded-lg border border-brand-200 transition-colors font-medium"
        >
          Ver todos los casos ({remaining} más)
          <ChevronRight size={14} />
        </button>
      )}
    </div>
  )
}

interface EmptyStateProps {
  icon: React.ComponentType<{ size?: number; className?: string }>
  title: string
  description: string
}

function EmptyState({ icon: Icon, title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-3">
        <Icon size={22} className="text-slate-400" />
      </div>
      <h3 className="text-sm font-semibold text-slate-600 mb-1">{title}</h3>
      <p className="text-xs text-slate-400 max-w-sm">{description}</p>
    </div>
  )
}

const CANAL_LABEL: Record<string, string> = {
  email: 'Email', sms: 'SMS', interno: 'Interno', sistema: 'Sistema',
}

const NOTIF_ESTADO_COLOR: Record<string, string> = {
  enviado: 'bg-green-50 text-green-700 border-green-200',
  pendiente: 'bg-amber-50 text-amber-700 border-amber-200',
  fallido: 'bg-red-50 text-red-700 border-red-200',
}

function NotificacionCard({ notificacion: n }: { notificacion: Notificacion }) {
  const stateClass = NOTIF_ESTADO_COLOR[n.estado] ?? 'bg-slate-100 text-slate-500 border-slate-200'
  const date = new Date(n.timestamp)
  const dateStr = date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
  const timeStr = date.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
            <Bell size={14} className="text-slate-500" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-semibold text-slate-800">{n.tipo}</span>
              <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                {CANAL_LABEL[n.canal] ?? n.canal}
              </span>
            </div>
            <p className="text-sm text-slate-600 mt-0.5 truncate">{n.destinatario}</p>
            {n.mensaje && (
              <p className="text-xs text-slate-400 mt-1 leading-relaxed line-clamp-2">{n.mensaje}</p>
            )}
            <p className="text-xs text-slate-400 mt-1">{dateStr} · {timeStr}</p>
          </div>
        </div>
        <span className={`text-xs font-medium px-2 py-1 rounded-full border flex-shrink-0 ${stateClass}`}>
          {n.estado}
        </span>
      </div>
    </div>
  )
}

function EquipoCard({ equipo }: { equipo: Equipo }) {
  const tipoLabel: Record<string, string> = {
    multifuncional_impresion: 'Multifuncional',
    impresora_produccion: 'Impresora Producción',
    colaboracion_audiovisual: 'Colaboración A/V',
    automatizacion_sala: 'Automatización Sala',
    audio_corporativo: 'Audio Corporativo',
    senalizacion_digital: 'Señalización Digital',
    videoconferencia: 'Videoconferencia',
  }
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-slate-100 rounded-lg flex items-center justify-center">
            <Monitor size={17} className="text-slate-500" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-slate-800">{equipo.serial}</span>
              <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                {tipoLabel[equipo.tipo] ?? equipo.tipo}
              </span>
            </div>
            <p className="text-sm text-slate-600 mt-0.5">{equipo.marca} {equipo.modelo}</p>
            {equipo.ubicacion_fisica && (
              <p className="text-xs text-slate-400 mt-1">{equipo.ubicacion_fisica}</p>
            )}
          </div>
        </div>
        <span className={`text-xs font-medium px-2 py-1 rounded-full border ${
          equipo.estado === 'activo'
            ? 'bg-green-50 text-green-700 border-green-200'
            : 'bg-slate-100 text-slate-500 border-slate-200'
        }`}>
          {equipo.estado ?? 'activo'}
        </span>
      </div>
    </div>
  )
}
