import { useState } from 'react'
import { X, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import { useProcesarDocumento } from '../../hooks/useSolicitudes'
import type { ProcesarDocumentoResult } from '../../types'

interface ProcesarDocumentoModalProps {
  onClose: () => void
  onSuccess: (message: string) => void
  onError: (message: string) => void
}

const FIXTURES = [
  'fixtures/pdfs/acta_entrega_kyocera_001.pdf',
  'fixtures/pdfs/acta_entrega_barco_001.pdf',
  'fixtures/pdfs/orden_servicio_bose_001.pdf',
  'fixtures/pdfs/orden_garantia_crestron_001.pdf',
  'fixtures/pdfs/acta_entrega_lg_001.pdf',
]

const ACCION_LABEL: Record<string, string> = {
  CREAR_SOLICITUD: 'Crear solicitud',
  ACTUALIZAR_ESTADO: 'Actualizar estado',
  NOTIFICAR: 'Notificar',
  ESCALAR: 'Escalar',
}

export function ProcesarDocumentoModal({ onClose, onSuccess, onError }: ProcesarDocumentoModalProps) {
  const [pdfPath, setPdfPath] = useState(FIXTURES[0])
  const [result, setResult] = useState<ProcesarDocumentoResult | null>(null)
  const procesarMutation = useProcesarDocumento()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!pdfPath.trim()) {
      onError('Selecciona o ingresa una ruta de PDF')
      return
    }
    try {
      const res = await procesarMutation.mutateAsync(pdfPath.trim())
      setResult(res)
      const label = ACCION_LABEL[res.accion] ?? res.accion
      onSuccess(`Documento procesado: acción "${label}" ejecutada con ${Math.round(res.confianza * 100)}% de confianza`)
    } catch {
      onError('Error al procesar el documento. Verifica que el PDF existe en el servidor.')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-brand-50 rounded-lg flex items-center justify-center">
              <FileText size={16} className="text-brand-600" />
            </div>
            <h2 className="text-base font-semibold text-slate-800">Procesar Documento PDF</h2>
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
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1.5">
              PDF de fixture (ruta en el servidor)
            </label>
            <select
              value={pdfPath}
              onChange={(e) => setPdfPath(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white"
            >
              {FIXTURES.map((f) => (
                <option key={f} value={f}>
                  {f.replace('fixtures/pdfs/', '')}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1.5">
              O ingresa una ruta personalizada
            </label>
            <input
              type="text"
              value={pdfPath}
              onChange={(e) => setPdfPath(e.target.value)}
              placeholder="fixtures/pdfs/acta_entrega_kyocera_001.pdf"
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          {/* Result */}
          {result && (
            <div className="bg-slate-50 rounded-lg border border-slate-200 p-4 space-y-2">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle size={15} className="text-green-600" />
                <span className="text-sm font-semibold text-slate-800">Resultado del procesamiento</span>
              </div>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
                <span className="text-slate-500">Acción</span>
                <span className="font-medium text-slate-800">{ACCION_LABEL[result.accion] ?? result.accion}</span>
                <span className="text-slate-500">Confianza</span>
                <span className="font-medium text-slate-800">{Math.round(result.confianza * 100)}%</span>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-1">Razonamiento</p>
                <p className="text-xs text-slate-700 leading-relaxed">{result.razonamiento}</p>
              </div>
              {result.solicitud_creada && (
                <div className="flex items-center gap-2 pt-1">
                  <AlertCircle size={13} className="text-brand-500" />
                  <span className="text-xs text-brand-700 font-medium">
                    Solicitud creada: #{result.solicitud_creada.id}
                  </span>
                </div>
              )}
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cerrar
            </button>
            <button
              type="submit"
              disabled={procesarMutation.isPending}
              className="px-4 py-2 text-sm font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors"
            >
              {procesarMutation.isPending ? 'Procesando...' : 'Procesar documento'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
