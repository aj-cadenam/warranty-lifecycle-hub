import { useState } from 'react'
import { X, Monitor } from 'lucide-react'
import { useCrearEquipo } from '../../hooks/useEquipos'
import type { NuevoEquipoData } from '../../types'

interface NuevoEquipoModalProps {
  onClose: () => void
  onSuccess: (message: string) => void
  onError: (message: string) => void
}

const TIPOS_EQUIPO = [
  { value: 'multifuncional_impresion', label: 'Multifuncional Impresión (Kyocera)' },
  { value: 'impresora_produccion', label: 'Impresora Producción (OCÉ)' },
  { value: 'colaboracion_audiovisual', label: 'Colaboración Audiovisual (Barco)' },
  { value: 'automatizacion_sala', label: 'Automatización de Sala (Crestron)' },
  { value: 'audio_corporativo', label: 'Audio Corporativo (Bose)' },
  { value: 'senalizacion_digital', label: 'Señalización Digital (LG)' },
  { value: 'videoconferencia', label: 'Videoconferencia' },
]

const EMPTY: NuevoEquipoData = {
  serial: '',
  nombre: '',
  marca: '',
  modelo: '',
  tipo: 'multifuncional_impresion',
  ubicacion_fisica: '',
}

export function NuevoEquipoModal({ onClose, onSuccess, onError }: NuevoEquipoModalProps) {
  const [form, setForm] = useState<NuevoEquipoData>(EMPTY)
  const crearEquipo = useCrearEquipo()

  const set = (field: keyof NuevoEquipoData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => setForm((prev) => ({ ...prev, [field]: e.target.value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.serial.trim() || !form.nombre.trim() || !form.marca.trim() || !form.modelo.trim()) {
      onError('Completa los campos obligatorios')
      return
    }
    try {
      const equipo = await crearEquipo.mutateAsync(form)
      onSuccess(`Equipo ${equipo.serial} registrado exitosamente`)
    } catch {
      onError('Error al registrar el equipo. Verifica que el serial no esté duplicado.')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-brand-100 rounded-lg flex items-center justify-center">
              <Monitor size={16} className="text-brand-600" />
            </div>
            <h2 className="text-base font-semibold text-slate-800">Registrar Equipo</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X size={16} className="text-slate-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-xs font-medium text-slate-600 mb-1.5">
                Serial <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.serial}
                onChange={set('serial')}
                placeholder="KYO-TASKalfa-2021-001"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <div className="col-span-2">
              <label className="block text-xs font-medium text-slate-600 mb-1.5">
                Nombre <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.nombre}
                onChange={set('nombre')}
                placeholder="Impresora multifuncional área administrativa"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">
                Marca <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.marca}
                onChange={set('marca')}
                placeholder="Kyocera"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">
                Modelo <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.modelo}
                onChange={set('modelo')}
                placeholder="TASKalfa 2553ci"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <div className="col-span-2">
              <label className="block text-xs font-medium text-slate-600 mb-1.5">Tipo de equipo</label>
              <select
                value={form.tipo}
                onChange={set('tipo')}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white"
              >
                {TIPOS_EQUIPO.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="col-span-2">
              <label className="block text-xs font-medium text-slate-600 mb-1.5">Ubicación física</label>
              <input
                type="text"
                value={form.ubicacion_fisica}
                onChange={set('ubicacion_fisica')}
                placeholder="Piso 3 - Área Administrativa"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={crearEquipo.isPending}
              className="px-4 py-2 text-sm font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors"
            >
              {crearEquipo.isPending ? 'Registrando...' : 'Registrar equipo'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
