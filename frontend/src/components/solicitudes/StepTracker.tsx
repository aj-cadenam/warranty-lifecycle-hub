import { Check } from 'lucide-react'
import type { EstadoSolicitud } from '../../types'

const STEPS: { key: EstadoSolicitud; label: string }[] = [
  { key: 'nueva', label: 'Nueva' },
  { key: 'validada', label: 'Validada' },
  { key: 'despachada', label: 'Despachada' },
  { key: 'en_reparacion', label: 'En Reparación' },
  { key: 'devuelta', label: 'Devuelta' },
  { key: 'cerrada', label: 'Cerrada' },
]

const STEP_ORDER: Record<EstadoSolicitud, number> = {
  nueva: 0,
  validada: 1,
  despachada: 2,
  en_reparacion: 3,
  devuelta: 4,
  cerrada: 5,
}

interface StepTrackerProps {
  estado: EstadoSolicitud
}

export function StepTracker({ estado }: StepTrackerProps) {
  const currentIndex = STEP_ORDER[estado] ?? 0

  return (
    <div className="flex items-center w-full mt-4 px-1">
      {STEPS.map((step, index) => {
        const isCompleted = index < currentIndex
        const isCurrent = index === currentIndex
        const isFuture = index > currentIndex

        return (
          <div key={step.key} className="flex items-center flex-1 last:flex-none">
            <div className="flex flex-col items-center">
              <div
                className={`
                  w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold transition-all
                  ${isCompleted ? 'bg-brand-600 text-white' : ''}
                  ${isCurrent ? 'bg-brand-600 text-white ring-4 ring-blue-100' : ''}
                  ${isFuture ? 'bg-slate-200 text-slate-400' : ''}
                `}
              >
                {isCompleted ? (
                  <Check size={14} strokeWidth={2.5} />
                ) : (
                  <span>{index + 1}</span>
                )}
              </div>
              <span
                className={`
                  mt-1.5 text-xs font-medium whitespace-nowrap
                  ${isCompleted || isCurrent ? 'text-brand-600' : 'text-slate-400'}
                `}
              >
                {step.label}
              </span>
            </div>
            {index < STEPS.length - 1 && (
              <div
                className={`
                  flex-1 h-0.5 mx-1 mb-4 transition-all
                  ${isCompleted ? 'bg-brand-600' : 'bg-slate-200'}
                `}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
