import { useState } from 'react'
import { ChevronDown, ChevronUp, ArrowRight, Clock, Cpu } from 'lucide-react'
import type { SolicitudGarantia, EstadoSolicitud } from '../../types'
import { SolicitudTimeline } from './SolicitudTimeline'
import { StepTracker } from './StepTracker'
import { useActualizarEstado } from '../../hooks/useSolicitudes'

// ── State flow config ──────────────────────────────────────

const STEP_KEYS: EstadoSolicitud[] = ['nueva', 'validada', 'despachada', 'en_reparacion', 'devuelta', 'cerrada']

const ESTADO_CONFIG: Record<EstadoSolicitud, { label: string; color: string; dot: string }> = {
  nueva:         { label: 'Nueva',         color: 'text-amber-700 bg-amber-50 border-amber-200',    dot: 'bg-amber-400' },
  validada:      { label: 'Validada',      color: 'text-blue-700 bg-blue-50 border-blue-200',       dot: 'bg-blue-500' },
  despachada:    { label: 'Despachada',    color: 'text-purple-700 bg-purple-50 border-purple-200', dot: 'bg-purple-500' },
  en_reparacion: { label: 'En Reparación', color: 'text-orange-700 bg-orange-50 border-orange-200', dot: 'bg-orange-500' },
  devuelta:      { label: 'Devuelta',      color: 'text-teal-700 bg-teal-50 border-teal-200',       dot: 'bg-teal-500' },
  cerrada:       { label: 'Cerrada',       color: 'text-slate-500 bg-slate-100 border-slate-200',   dot: 'bg-slate-400' },
}

const NEXT_ACTION: Partial<Record<EstadoSolicitud, { label: string; next: EstadoSolicitud }>> = {
  nueva:         { label: 'Validar',          next: 'validada' },
  validada:      { label: 'Despachar',        next: 'despachada' },
  en_reparacion: { label: 'Marcar devuelta',  next: 'devuelta' },
  devuelta:      { label: 'Cerrar',           next: 'cerrada' },
}

const URGENCY_BORDER: Record<string, string> = {
  red:   'border-l-4 border-l-red-400',
  amber: 'border-l-4 border-l-amber-400',
  green: 'border-l-4 border-l-green-400',
  slate: 'border-l-4 border-l-slate-200',
}

function getDaysElapsed(fechaReporte: string): number {
  const normalized = fechaReporte.includes('T') ? fechaReporte : `${fechaReporte}T00:00`
  return Math.max(0, Math.floor((Date.now() - new Date(normalized).getTime()) / 86400000))
}

function getUrgency(estado: EstadoSolicitud, days: number) {
  if (estado === 'cerrada') return 'slate'
  if (days > 14) return 'red'
  if (days > 7) return 'amber'
  return 'green'
}

// ── Mini state progress (always visible) ──────────────────

function MiniFlow({ estado }: { estado: EstadoSolicitud }) {
  const currentIdx = STEP_KEYS.indexOf(estado)
  const labels = ['N', 'V', 'D', 'R', 'Dev', 'Cer']
  return (
    <div className="flex items-center gap-0.5">
      {STEP_KEYS.map((key, i) => (
        <div key={key} className="flex items-center gap-0.5">
          <div
            title={ESTADO_CONFIG[key].label}
            className={`w-2 h-2 rounded-full flex-shrink-0 transition-colors ${
              i < currentIdx
                ? 'bg-brand-400'
                : i === currentIdx
                ? ESTADO_CONFIG[estado].dot
                : 'bg-slate-200'
            }`}
          />
          {i < STEP_KEYS.length - 1 && (
            <div className={`w-3 h-px flex-shrink-0 ${i < currentIdx ? 'bg-brand-300' : 'bg-slate-200'}`} />
          )}
        </div>
      ))}
      <span className="ml-1.5 text-xs text-slate-400 tabular-nums">
        {labels[currentIdx]}/{labels[STEP_KEYS.length - 1]}
      </span>
    </div>
  )
}

// ── Card ───────────────────────────────────────────────────

interface SolicitudCardProps {
  solicitud: SolicitudGarantia
}

export function SolicitudCard({ solicitud }: SolicitudCardProps) {
  const [expanded, setExpanded] = useState(false)
  const actualizarMutation = useActualizarEstado()

  const days = getDaysElapsed(solicitud.fecha_reporte)
  const urgency = getUrgency(solicitud.estado, days)
  const nextAction = NEXT_ACTION[solicitud.estado]
  const estadoConf = ESTADO_CONFIG[solicitud.estado]

  const equipoLabel = solicitud.equipo
    ? `${solicitud.equipo.serial} · ${solicitud.equipo.marca} ${solicitud.equipo.modelo}`
    : solicitud.equipo_id

  const handleAdvance = async (e: React.MouseEvent) => {
    e.stopPropagation()
    if (!nextAction) return
    await actualizarMutation.mutateAsync({ id: solicitud.id, estado: nextAction.next })
  }

  return (
    <div className={`bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden ${URGENCY_BORDER[urgency]}`}>
      {/* Main row — always visible */}
      <div
        className="px-4 py-3 cursor-pointer select-none"
        onClick={() => setExpanded(!expanded)}
      >
        {/* Top: equipo + estado + dias */}
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex items-center gap-2 min-w-0">
            <Cpu size={13} className="text-slate-400 flex-shrink-0 mt-0.5" />
            <span className="text-sm font-semibold text-slate-800 truncate">{equipoLabel}</span>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            {/* Urgency días badge */}
            {solicitud.estado !== 'cerrada' && (
              <span className={`flex items-center gap-1 text-xs font-medium px-1.5 py-0.5 rounded-full ${
                urgency === 'red'   ? 'bg-red-50 text-red-600' :
                urgency === 'amber' ? 'bg-amber-50 text-amber-600' :
                                     'bg-slate-100 text-slate-500'
              }`}>
                <Clock size={10} />
                {days}d
              </span>
            )}
            {/* Estado badge */}
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${estadoConf.color}`}>
              {estadoConf.label}
            </span>
            {expanded ? <ChevronUp size={14} className="text-slate-400" /> : <ChevronDown size={14} className="text-slate-400" />}
          </div>
        </div>

        {/* Description */}
        {solicitud.descripcion_falla && (
          <p className="text-xs text-slate-500 truncate mb-2.5 pl-5">
            {solicitud.descripcion_falla.replace(/^ACTA DE ENTREGA[^.]*\n?/i, '').trim().split('\n')[0]}
          </p>
        )}

        {/* Bottom: mini flow + action */}
        <div className="flex items-center justify-between pl-5">
          <MiniFlow estado={solicitud.estado} />
          {nextAction && (
            <button
              onClick={handleAdvance}
              disabled={actualizarMutation.isPending}
              className="flex items-center gap-1 text-xs font-medium text-brand-600 hover:text-brand-700 hover:bg-brand-50 px-2 py-1 rounded-lg transition-colors disabled:opacity-50"
            >
              {nextAction.label}
              <ArrowRight size={11} />
            </button>
          )}
        </div>
      </div>

      {/* Expanded: step tracker + timeline */}
      {expanded && (
        <div className="border-t border-slate-100 px-4 pb-4">
          <StepTracker estado={solicitud.estado} />
          <div className="mt-4">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">Historial</p>
            <SolicitudTimeline solicitud={solicitud} />
          </div>
        </div>
      )}
    </div>
  )
}
