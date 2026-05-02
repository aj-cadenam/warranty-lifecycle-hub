import { X, Sparkles, Shield } from 'lucide-react'
import type { BuscarResultado } from '../../types'

const ESTADO_COLOR: Record<string, string> = {
  nueva: 'bg-brand-50 text-brand-700 border-brand-200',
  validada: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  despachada: 'bg-amber-50 text-amber-700 border-amber-200',
  en_reparacion: 'bg-orange-50 text-orange-700 border-orange-200',
  devuelta: 'bg-purple-50 text-purple-700 border-purple-200',
  cerrada: 'bg-green-50 text-green-700 border-green-200',
}

interface BuscarSimilaresModalProps {
  query: string
  resultados: BuscarResultado[]
  onClose: () => void
}

export function BuscarSimilaresModal({ query, resultados, onClose }: BuscarSimilaresModalProps) {
  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-xl flex flex-col max-h-[80vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-brand-500 to-brand-700 rounded-lg flex items-center justify-center">
              <Sparkles size={15} className="text-white" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-800">Casos similares</h2>
              <p className="text-xs text-slate-400 mt-0.5 max-w-xs truncate">
                "{query}"
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X size={16} className="text-slate-500" />
          </button>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {resultados.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-3">
                <Shield size={20} className="text-slate-400" />
              </div>
              <p className="text-sm font-semibold text-slate-600 mb-1">Sin resultados</p>
              <p className="text-xs text-slate-400 max-w-xs">
                El agente no encontró casos similares para esta consulta. Intenta con otros términos.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-xs text-slate-400 mb-4">
                {resultados.length} {resultados.length === 1 ? 'caso encontrado' : 'casos encontrados'} por búsqueda semántica
              </p>
              {resultados.map((s) => (
                <ResultCard key={s.id} solicitud={s} />
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-100 flex-shrink-0">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  )
}

function ResultCard({ solicitud: s }: { solicitud: BuscarResultado }) {
  const stateClass = ESTADO_COLOR[s.estado] ?? 'bg-slate-100 text-slate-500 border-slate-200'
  const date = new Date(s.fecha_reporte).toLocaleDateString('es-CO', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
  const similitud = Math.round(s.similitud * 100)

  return (
    <div className="bg-slate-50 rounded-lg border border-slate-200 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="text-xs font-mono text-slate-400">#{s.id.slice(0, 8)}</span>
            <span className="text-xs font-medium text-slate-700">{s.equipo_id}</span>
            <span className="text-xs text-brand-600 bg-brand-50 px-1.5 py-0.5 rounded border border-brand-100">
              {similitud}%
            </span>
          </div>
          <p className="text-sm text-slate-700 leading-snug line-clamp-2">
            {s.descripcion_falla}
          </p>
          <p className="text-xs text-slate-400 mt-1.5">{date}</p>
        </div>
        <span className={`text-xs font-medium px-2 py-1 rounded-full border flex-shrink-0 ${stateClass}`}>
          {s.estado.replace('_', ' ')}
        </span>
      </div>
    </div>
  )
}
