import { useState, useEffect } from 'react'
import { Plus, RefreshCw, Search, Shield, Monitor, Inbox, CheckSquare, FileText, Bell, Bot, Sparkles, PanelRightClose, PanelRightOpen } from 'lucide-react'
import type { NavSection, SolicitudGarantia, BorradorCorreo, Equipo, Notificacion } from '../../types'
import { SolicitudCard } from '../solicitudes/SolicitudCard'
import { BorradorCard } from '../borradores/BorradorCard'
import { SolicitudCardSkeleton } from '../ui/Skeleton'
import { useVerificarSemanal } from '../../hooks/useSolicitudes'
import { api } from '../../api/client'
import { NewSolicitudModal } from './NewSolicitudModal'
import { NuevoEquipoModal } from '../equipos/NuevoEquipoModal'
import { ProcesarDocumentoModal } from '../agente/ProcesarDocumentoModal'
import { AgentChat } from '../agent/AgentChat'

const SECTION_TITLES: Record<NavSection, string> = {
  dashboard: 'Dashboard',
  garantias: 'Solicitudes de Garantía',
  equipos: 'Equipos',
  borradores: 'Borradores de Correo',
  verificar: 'Verificación Semanal',
  notificaciones: 'Notificaciones',
}

interface CenterPanelProps {
  activeSection: NavSection
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
  const [showChat, setShowChat] = useState(true)
  const [showNewSolicitudModal, setShowNewSolicitudModal] = useState(false)
  const [showNuevoEquipoModal, setShowNuevoEquipoModal] = useState(false)
  const [showProcesarDocumentoModal, setShowProcesarDocumentoModal] = useState(false)
  const [llmProvider, setLlmProvider] = useState('...')
  const verificarMutation = useVerificarSemanal()

  useEffect(() => {
    api.getHealth().then(h => setLlmProvider(h.llm_provider)).catch(() => setLlmProvider('?'))
  }, [])
  const providerLabel = llmProvider === 'gemini' ? 'Gemini · Real' : llmProvider === '...' ? 'Gemini · ...' : 'Gemini · Mock mode'

  const title = SECTION_TITLES[activeSection]

  const handleVerificarSemanal = async () => {
    try {
      const result = await verificarMutation.mutateAsync()
      onToast(
        `Verificación completada: ${result.solicitudes_verificadas} solicitudes, ${result.borradores_generados} borradores generados`,
        'success'
      )
    } catch {
      onToast('Error al ejecutar la verificación semanal', 'error')
    }
  }

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
              {activeSection === 'garantias' && `${solicitudes.length} solicitudes totales`}
              {activeSection === 'borradores' && `${borradores.filter(b => b.estado === 'pendiente_aprobacion').length} pendientes de aprobación`}
              {activeSection === 'equipos' && `${equipos.length} equipos registrados`}
              {activeSection === 'dashboard' && 'Vista general del sistema'}
              {activeSection === 'verificar' && 'Verifica el estado de garantías activas'}
              {activeSection === 'notificaciones' && `${notificaciones.length} notificaciones`}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* LLM AI toggle — only relevant on dashboard */}
            {activeSection === 'dashboard' && (
              <button
                onClick={() => setShowChat((v) => !v)}
                title={showChat ? 'Ocultar Agente IA' : 'Mostrar Agente IA'}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all border ${
                  showChat
                    ? 'bg-brand-600 text-white border-brand-600 hover:bg-brand-700 shadow-sm shadow-brand-200'
                    : 'border-slate-300 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Sparkles size={14} className={showChat ? 'text-white' : 'text-brand-500'} />
                <span>LLM IA</span>
                {showChat
                  ? <PanelRightClose size={13} className="ml-0.5 opacity-80" />
                  : <PanelRightOpen size={13} className="ml-0.5 text-slate-400" />
                }
              </button>
            )}
            <button
              onClick={() => setShowProcesarDocumentoModal(true)}
              className="flex items-center gap-1.5 px-3 py-2 border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors"
            >
              <FileText size={14} />
              Procesar PDF
            </button>
            <button
              onClick={handleVerificarSemanal}
              disabled={verificarMutation.isPending}
              className="flex items-center gap-1.5 px-3 py-2 border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors disabled:opacity-50"
            >
              <RefreshCw size={14} className={verificarMutation.isPending ? 'animate-spin' : ''} />
              Verificar Semanal
            </button>
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

      {/* Content area — dashboard is two-column, others are single scroll */}
      {activeSection === 'dashboard' ? (
        <div className="flex-1 overflow-hidden flex">
          {/* Left: stats + recent */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
            <div className="grid grid-cols-3 gap-4">
              <StatCard
                icon={Shield}
                label="Total solicitudes"
                value={solicitudes.length}
                subLabel={`${solicitudes.filter(s => s.estado !== 'cerrada').length} activas`}
                color="blue"
              />
              <StatCard
                icon={Inbox}
                label="Borradores pendientes"
                value={borradores.filter(b => b.estado === 'pendiente_aprobacion').length}
                subLabel="Requieren aprobación"
                color={borradores.filter(b => b.estado === 'pendiente_aprobacion').length > 0 ? 'amber' : 'slate'}
              />
              <StatCard
                icon={CheckSquare}
                label="Solicitudes cerradas"
                value={solicitudes.filter(s => s.estado === 'cerrada').length}
                subLabel="Resueltas"
                color="green"
              />
            </div>

            <div>
              <h3 className="text-sm font-semibold text-slate-700 mb-3">Solicitudes recientes</h3>
              {isLoadingSolicitudes ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => <SolicitudCardSkeleton key={i} />)}
                </div>
              ) : solicitudes.length === 0 ? (
                <EmptyState
                  icon={Shield}
                  title="Sin solicitudes"
                  description="No hay solicitudes registradas. El backend puede estar iniciando."
                />
              ) : (
                <div className="space-y-3">
                  {solicitudes.slice(0, 5).map((s) => (
                    <SolicitudCard key={s.id} solicitud={s} />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right: embedded agent chat */}
          {showChat && <div className="w-80 flex-shrink-0 border-l border-slate-200 flex flex-col bg-white">
            <div className="px-4 py-3 border-b border-slate-100 flex-shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 bg-gradient-to-br from-brand-500 to-brand-700 rounded-lg flex items-center justify-center">
                  <Bot size={15} className="text-white" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-slate-800">Agente IA</span>
                    <div className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse-dot" />
                      <span className="text-xs text-green-600 font-medium">Activo</span>
                    </div>
                  </div>
                  <p className="text-xs text-slate-400">{providerLabel}</p>
                </div>
              </div>
            </div>
            <div className="flex-1 overflow-hidden">
              <AgentChat
                solicitudes={solicitudes}
                borradores={borradores}
                onToast={onToast}
              />
            </div>
          </div>}
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto px-6 py-4">

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

          {/* VERIFICAR */}
          {activeSection === 'verificar' && (
            <div className="max-w-lg mx-auto text-center py-12">
              <div className="w-16 h-16 bg-brand-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <RefreshCw size={28} className="text-brand-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-800 mb-2">Verificación Semanal</h3>
              <p className="text-slate-500 text-sm mb-6 leading-relaxed">
                Verifica el estado de todas las solicitudes activas. Para cada solicitud sin respuesta
                del proveedor o cliente que supere el timeout configurado, se generará un borrador de
                seguimiento automáticamente.
              </p>
              <div className="bg-slate-50 rounded-lg p-4 border border-slate-200 mb-6 text-left space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Timeout proveedor</span>
                  <span className="font-medium text-slate-800">7 días</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Timeout cliente</span>
                  <span className="font-medium text-slate-800">7 días</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Solicitudes activas</span>
                  <span className="font-medium text-slate-800">
                    {solicitudes.filter(s => ['despachada', 'en_reparacion'].includes(s.estado)).length}
                  </span>
                </div>
              </div>
              <button
                onClick={handleVerificarSemanal}
                disabled={verificarMutation.isPending}
                className="inline-flex items-center gap-2 px-6 py-3 bg-brand-600 text-white rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50 transition-colors"
              >
                <RefreshCw size={16} className={verificarMutation.isPending ? 'animate-spin' : ''} />
                {verificarMutation.isPending ? 'Verificando...' : 'Ejecutar verificación'}
              </button>
            </div>
          )}
        </div>
      )}

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

interface StatCardProps {
  icon: React.ComponentType<{ size?: number; className?: string }>
  label: string
  value: number
  subLabel: string
  color: 'blue' | 'amber' | 'green' | 'slate'
}

function StatCard({ icon: Icon, label, value, subLabel, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-brand-50 text-brand-600',
    amber: 'bg-amber-50 text-amber-600',
    green: 'bg-green-50 text-green-600',
    slate: 'bg-slate-100 text-slate-500',
  }
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
          <Icon size={18} />
        </div>
      </div>
      <p className="text-3xl font-bold text-brand-600">{value}</p>
      <p className="text-sm font-semibold text-slate-700 mt-1">{label}</p>
      <p className="text-xs text-slate-400 mt-0.5">{subLabel}</p>
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
