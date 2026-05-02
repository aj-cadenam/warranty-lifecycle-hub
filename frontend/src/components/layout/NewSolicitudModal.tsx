import { useState } from 'react'
import { X, Plus } from 'lucide-react'
import type { Equipo } from '../../types'
import { useCrearSolicitud } from '../../hooks/useSolicitudes'

interface NewSolicitudModalProps {
  equipos: Equipo[]
  onClose: () => void
  onSuccess: (message: string) => void
  onError: (message: string) => void
}

export function NewSolicitudModal({ equipos, onClose, onSuccess, onError }: NewSolicitudModalProps) {
  const [equipoId, setEquipoId] = useState('')
  const [reportadoPor, setReportadoPor] = useState('javiercadena63@gmail.com')
  const [descripcionFalla, setDescripcionFalla] = useState('')

  const crearMutation = useCrearSolicitud()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!equipoId || !reportadoPor || !descripcionFalla) return

    try {
      await crearMutation.mutateAsync({
        equipo_id: equipoId,
        reportado_por: reportadoPor,
        descripcion_falla: descripcionFalla,
      })
      onSuccess('Solicitud de garantía creada correctamente')
    } catch (err) {
      onError('Error al crear la solicitud. Verifica que el equipo exista.')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="font-semibold text-slate-800">Nueva Solicitud de Garantía</h3>
            <p className="text-xs text-slate-500 mt-0.5">Registro manual de falla</p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Equipo */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Equipo *
            </label>
            {equipos.length > 0 ? (
              <select
                value={equipoId}
                onChange={(e) => setEquipoId(e.target.value)}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Seleccionar equipo...</option>
                {equipos.map((eq) => (
                  <option key={eq.id} value={eq.id}>
                    {eq.serial} — {eq.marca} {eq.modelo}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value={equipoId}
                onChange={(e) => setEquipoId(e.target.value)}
                placeholder="ID o serial del equipo"
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            )}
          </div>

          {/* Reportado por */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Reportado por *
            </label>
            <input
              type="text"
              value={reportadoPor}
              onChange={(e) => setReportadoPor(e.target.value)}
              placeholder="Email o nombre"
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          {/* Descripción de falla */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Descripción de la falla *
            </label>
            <textarea
              value={descripcionFalla}
              onChange={(e) => setDescripcionFalla(e.target.value)}
              placeholder="Describe el problema del equipo..."
              rows={3}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
            />
          </div>

          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={!equipoId || !reportadoPor || !descripcionFalla || crearMutation.isPending}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 disabled:opacity-50 transition-colors"
            >
              {crearMutation.isPending ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Plus size={15} />
              )}
              Crear solicitud
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
