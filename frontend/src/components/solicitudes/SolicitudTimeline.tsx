import { Bot, User, Mail, CheckCircle, AlertCircle, Package } from 'lucide-react'
import type { SolicitudGarantia } from '../../types'

interface TimelineEvent {
  id: string
  type: 'agente' | 'usuario' | 'email' | 'estado' | 'sistema' | 'alerta'
  title: string
  description?: string
  timestamp: string
  details?: string[]
}

function buildTimeline(solicitud: SolicitudGarantia): TimelineEvent[] {
  const events: TimelineEvent[] = []

  // Creation event
  events.push({
    id: 'created',
    type: 'agente',
    title: 'Solicitud creada',
    description: `Reportado por: ${solicitud.reportado_por}`,
    timestamp: solicitud.created_at,
    details: solicitud.descripcion_falla ? [`Falla: ${solicitud.descripcion_falla}`] : undefined,
  })

  // Trazabilidad events
  if (solicitud.eventos && solicitud.eventos.length > 0) {
    solicitud.eventos.forEach((evento) => {
      events.push({
        id: evento.id,
        type: evento.metodo_registro === 'agente' ? 'agente' : 'usuario',
        title: `Movimiento: ${evento.ubicacion_anterior} → ${evento.ubicacion_nueva}`,
        description: evento.descripcion,
        timestamp: evento.created_at,
      })
    })
  }

  // State changes based on current state
  const stateOrder = ['nueva', 'validada', 'despachada', 'en_reparacion', 'devuelta', 'cerrada']
  const currentIndex = stateOrder.indexOf(solicitud.estado)

  for (let i = 1; i <= currentIndex; i++) {
    const estado = stateOrder[i]
    events.push({
      id: `state-${estado}`,
      type: 'estado',
      title: `Estado actualizado: ${formatEstado(estado)}`,
      timestamp: solicitud.updated_at,
    })
  }

  return events.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
}

function formatEstado(estado: string): string {
  const labels: Record<string, string> = {
    nueva: 'Nueva',
    validada: 'Validada',
    despachada: 'Despachada → Proveedor',
    en_reparacion: 'En Reparación',
    devuelta: 'Devuelta al cliente',
    cerrada: 'Cerrada',
  }
  return labels[estado] ?? estado
}

function formatTime(dateStr: string): string {
  try {
    const date = new Date(dateStr)
    return date.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
  } catch {
    return dateStr
  }
}

const eventIconMap = {
  agente: { Icon: Bot, color: 'bg-brand-100 text-brand-600', dotColor: 'bg-brand-500' },
  usuario: { Icon: User, color: 'bg-slate-100 text-slate-600', dotColor: 'bg-slate-400' },
  email: { Icon: Mail, color: 'bg-purple-100 text-purple-600', dotColor: 'bg-purple-500' },
  estado: { Icon: CheckCircle, color: 'bg-green-100 text-green-600', dotColor: 'bg-green-500' },
  sistema: { Icon: Package, color: 'bg-slate-100 text-slate-500', dotColor: 'bg-slate-300' },
  alerta: { Icon: AlertCircle, color: 'bg-orange-100 text-orange-600', dotColor: 'bg-orange-500' },
}

interface SolicitudTimelineProps {
  solicitud: SolicitudGarantia
}

export function SolicitudTimeline({ solicitud }: SolicitudTimelineProps) {
  const events = buildTimeline(solicitud)

  if (events.length === 0) {
    return (
      <div className="py-4 text-center text-slate-400 text-sm">
        Sin eventos registrados
      </div>
    )
  }

  return (
    <div className="space-y-0 pt-2">
      {events.map((event, index) => {
        const { Icon, color } = eventIconMap[event.type]
        const isLast = index === events.length - 1

        return (
          <div key={event.id} className="flex gap-3">
            {/* Timeline connector column */}
            <div className="flex flex-col items-center flex-shrink-0">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center ${color} flex-shrink-0 z-10`}>
                <Icon size={14} />
              </div>
              {!isLast && (
                <div className="w-0.5 flex-1 bg-slate-200 my-1" style={{ minHeight: '16px' }} />
              )}
            </div>

            {/* Content */}
            <div className={`flex-1 ${isLast ? 'pb-2' : 'pb-3'}`}>
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm font-medium text-slate-800">{event.title}</p>
                <span className="text-xs text-slate-400 whitespace-nowrap flex-shrink-0">
                  {formatTime(event.timestamp)}
                </span>
              </div>
              {event.description && (
                <p className="text-xs text-slate-500 mt-0.5">{event.description}</p>
              )}
              {event.details && event.details.length > 0 && (
                <ul className="mt-1 space-y-0.5">
                  {event.details.map((detail, i) => (
                    <li key={i} className="text-xs text-slate-500 flex items-start gap-1">
                      <span className="text-brand-400 font-bold mt-0.5">→</span>
                      {detail}
                    </li>
                  ))}
                </ul>
              )}
              <p className="text-xs text-slate-400 mt-1">{formatDate(event.timestamp)}</p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
