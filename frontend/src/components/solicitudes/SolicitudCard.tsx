import { useState } from 'react'
import { ChevronDown, ChevronUp, Calendar, Cpu } from 'lucide-react'
import type { SolicitudGarantia } from '../../types'
import { SolicitudBadge } from '../ui/Badge'
import { SolicitudTimeline } from './SolicitudTimeline'
import { StepTracker } from './StepTracker'

function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
  } catch {
    return dateStr
  }
}

interface SolicitudCardProps {
  solicitud: SolicitudGarantia
}

export function SolicitudCard({ solicitud }: SolicitudCardProps) {
  const [expanded, setExpanded] = useState(false)

  const equipoLabel = solicitud.equipo
    ? `${solicitud.equipo.serial} · ${solicitud.equipo.marca} ${solicitud.equipo.modelo}`
    : solicitud.equipo_id

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
      {/* Card header */}
      <div
        className="p-4 cursor-pointer select-none"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 flex-wrap">
            <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
              solicitud.estado === 'nueva' ? 'bg-amber-400' :
              solicitud.estado === 'validada' ? 'bg-brand-400' :
              solicitud.estado === 'despachada' ? 'bg-purple-400' :
              solicitud.estado === 'en_reparacion' ? 'bg-orange-400' :
              solicitud.estado === 'devuelta' ? 'bg-teal-400' :
              'bg-slate-300'
            }`} />
            <SolicitudBadge estado={solicitud.estado} />
            <span className="text-sm font-semibold text-slate-700">
              Solicitud #{solicitud.id.slice(0, 8)}
            </span>
          </div>
          <div className="flex items-center gap-2 text-slate-400">
            <Calendar size={13} />
            <span className="text-xs">{formatDate(solicitud.created_at)}</span>
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-1.5">
          <Cpu size={13} className="text-slate-400" />
          <span>{equipoLabel}</span>
        </div>

        {solicitud.descripcion_falla && (
          <p className="text-sm text-slate-600 line-clamp-2 font-mono bg-slate-50 rounded px-2 py-1 text-xs border border-slate-100">
            "{solicitud.descripcion_falla}"
          </p>
        )}
      </div>

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-slate-100 bg-slate-50/50">
          {/* Step tracker */}
          <div className="px-4 pt-4 pb-2 overflow-x-auto">
            <StepTracker estado={solicitud.estado} />
          </div>

          {/* Timeline */}
          <div className="px-4 pt-3 pb-4">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
              Historial de eventos
            </h4>
            <SolicitudTimeline solicitud={solicitud} />
          </div>
        </div>
      )}
    </div>
  )
}
