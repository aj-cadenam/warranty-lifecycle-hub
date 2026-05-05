import { useState, useRef } from 'react'
import { X, FileText, CheckCircle, AlertCircle, Upload, FolderOpen } from 'lucide-react'
import { useProcesarDocumento, useUploadDocumento } from '../../hooks/useSolicitudes'
import type { ProcesarDocumentoResult } from '../../types'

interface ProcesarDocumentoModalProps {
  onClose: () => void
  onSuccess: (message: string) => void
  onError: (message: string) => void
}

const FIXTURES = [
  { label: 'Kyocera TASKalfa 2553ci', path: 'fixtures/pdfs/acta_entrega_kyo_taskalfa_2021_001.pdf' },
  { label: 'Barco ClickShare CX-50', path: 'fixtures/pdfs/acta_entrega_bar_cs_2022_014.pdf' },
  { label: 'Bose PowerMatch PM8500N', path: 'fixtures/pdfs/acta_entrega_bsp_pmx_2020_007.pdf' },
  { label: 'Crestron TSW-770', path: 'fixtures/pdfs/acta_entrega_cre_tsw_2023_003.pdf' },
  { label: 'LG 55SM5KE', path: 'fixtures/pdfs/acta_entrega_lg_mri_2022_021.pdf' },
]

const ACCION_LABEL: Record<string, string> = {
  CREAR_SOLICITUD: 'Crear solicitud',
  ACTUALIZAR_ESTADO: 'Actualizar estado',
  NOTIFICAR: 'Notificar',
  ESCALAR: 'Escalar',
}

export function ProcesarDocumentoModal({ onClose, onSuccess, onError }: ProcesarDocumentoModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [result, setResult] = useState<ProcesarDocumentoResult | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const uploadMutation = useUploadDocumento()
  const fixtureMutation = useProcesarDocumento()
  const isPending = uploadMutation.isPending || fixtureMutation.isPending

  const processResult = (res: ProcesarDocumentoResult) => {
    setResult(res)
    const label = ACCION_LABEL[res.accion] ?? res.accion
    onSuccess(`Documento procesado: acción "${label}" con ${Math.round(res.confianza * 100)}% de confianza`)
  }

  const handleFileChange = (file: File) => {
    if (!file.name.endsWith('.pdf')) {
      onError('Solo se aceptan archivos PDF')
      return
    }
    setSelectedFile(file)
    setResult(null)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFileChange(file)
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    try {
      const res = await uploadMutation.mutateAsync(selectedFile)
      processResult(res)
    } catch {
      onError('Error al procesar el archivo. Verifica que el backend está corriendo.')
    }
  }

  const handleFixture = async (path: string) => {
    setSelectedFile(null)
    setResult(null)
    try {
      const res = await fixtureMutation.mutateAsync(path)
      processResult(res)
    } catch {
      onError('Error al procesar el fixture.')
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-brand-50 rounded-lg flex items-center justify-center">
              <FileText size={14} className="text-brand-600" />
            </div>
            <h2 className="text-sm font-semibold text-slate-800">Procesar Documento PDF</h2>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X size={14} className="text-slate-500" />
          </button>
        </div>

        <div className="px-4 py-4 space-y-4">
          {/* Drop zone */}
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1.5">
              Subir PDF desde tu equipo
            </label>
            <div
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              className={`relative flex flex-col items-center justify-center gap-1.5 p-4 rounded-xl border-2 border-dashed cursor-pointer transition-colors ${
                isDragging
                  ? 'border-brand-400 bg-brand-50'
                  : selectedFile
                  ? 'border-green-400 bg-green-50'
                  : 'border-slate-300 hover:border-brand-400 hover:bg-slate-50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFileChange(f) }}
              />
              {selectedFile ? (
                <>
                  <CheckCircle size={18} className="text-green-500" />
                  <p className="text-sm font-medium text-green-700">{selectedFile.name}</p>
                  <p className="text-xs text-green-600">{(selectedFile.size / 1024).toFixed(1)} KB · listo para procesar</p>
                </>
              ) : (
                <>
                  <FolderOpen size={18} className="text-slate-400" />
                  <p className="text-sm text-slate-600">
                    <span className="font-medium text-brand-600">Haz clic para seleccionar</span> o arrastra aquí
                  </p>
                  <p className="text-xs text-slate-400">Solo archivos PDF</p>
                </>
              )}
            </div>

            {selectedFile && (
              <button
                onClick={handleUpload}
                disabled={isPending}
                className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors"
              >
                <Upload size={14} />
                {uploadMutation.isPending ? 'Procesando...' : 'Procesar archivo'}
              </button>
            )}
          </div>

          {/* Fixtures */}
          <div>
            <p className="text-xs font-medium text-slate-600 mb-1.5">O usa un fixture del servidor</p>
            <div className="space-y-1">
              {FIXTURES.map((f) => (
                <button
                  key={f.path}
                  onClick={() => handleFixture(f.path)}
                  disabled={isPending}
                  className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg border border-slate-200 hover:border-brand-300 hover:bg-brand-50 text-left transition-colors disabled:opacity-50 group"
                >
                  <FileText size={13} className="text-slate-400 group-hover:text-brand-500 flex-shrink-0" />
                  <span className="text-xs text-slate-700 group-hover:text-brand-700">{f.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Result */}
          {result && (
            <div className="bg-slate-50 rounded-lg border border-slate-200 p-3 space-y-1.5">
              <div className="flex items-center gap-2">
                <CheckCircle size={13} className="text-green-600" />
                <span className="text-xs font-semibold text-slate-800">Resultado</span>
              </div>
              <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-xs">
                <span className="text-slate-500">Acción</span>
                <span className="font-medium text-slate-800">{ACCION_LABEL[result.accion] ?? result.accion}</span>
                <span className="text-slate-500">Confianza</span>
                <span className="font-medium text-slate-800">{Math.round(result.confianza * 100)}%</span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">{result.razonamiento}</p>
              {result.solicitud_creada && (
                <div className="flex items-center gap-1.5">
                  <AlertCircle size={12} className="text-brand-500" />
                  <span className="text-xs text-brand-700 font-medium">
                    Solicitud #{result.solicitud_creada.id} creada
                  </span>
                </div>
              )}
            </div>
          )}

          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
