import type { EstadoSolicitud, EstadoBorrador } from '../../types'

const estadoSolicitudConfig: Record<EstadoSolicitud, { label: string; className: string }> = {
  nueva: { label: 'Nueva', className: 'bg-amber-100 text-amber-700 border-amber-200' },
  validada: { label: 'Validada', className: 'bg-brand-100 text-brand-700 border-brand-200' },
  despachada: { label: 'Despachada', className: 'bg-purple-100 text-purple-700 border-purple-200' },
  en_reparacion: { label: 'En Reparación', className: 'bg-orange-100 text-orange-700 border-orange-200' },
  devuelta: { label: 'Devuelta', className: 'bg-teal-100 text-teal-700 border-teal-200' },
  cerrada: { label: 'Cerrada', className: 'bg-slate-100 text-slate-600 border-slate-200' },
}

const estadoBorradorConfig: Record<EstadoBorrador, { label: string; className: string }> = {
  generado: { label: 'Generado', className: 'bg-slate-100 text-slate-600 border-slate-200' },
  pendiente_aprobacion: { label: 'Pendiente', className: 'bg-amber-100 text-amber-700 border-amber-200' },
  aprobado: { label: 'Aprobado', className: 'bg-brand-100 text-brand-700 border-brand-200' },
  enviado: { label: 'Enviado', className: 'bg-green-100 text-green-700 border-green-200' },
  rechazado: { label: 'Rechazado', className: 'bg-red-100 text-red-700 border-red-200' },
}

interface SolicitudBadgeProps {
  estado: EstadoSolicitud
}

interface BorradorBadgeProps {
  estado: EstadoBorrador
}

export function SolicitudBadge({ estado }: SolicitudBadgeProps) {
  const config = estadoSolicitudConfig[estado] ?? {
    label: estado,
    className: 'bg-slate-100 text-slate-600 border-slate-200',
  }
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.className}`}
    >
      {config.label}
    </span>
  )
}

export function BorradorBadge({ estado }: BorradorBadgeProps) {
  const config = estadoBorradorConfig[estado] ?? {
    label: estado,
    className: 'bg-slate-100 text-slate-600 border-slate-200',
  }
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.className}`}
    >
      {config.label}
    </span>
  )
}
