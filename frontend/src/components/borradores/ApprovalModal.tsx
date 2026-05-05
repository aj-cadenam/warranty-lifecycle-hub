import { useState } from 'react'
import { X, CheckCircle, XCircle } from 'lucide-react'
import type { BorradorCorreo } from '../../types'

interface ApproveModalProps {
  borrador: BorradorCorreo
  onConfirm: (aprobadoPor: string) => void
  onCancel: () => void
  isLoading?: boolean
}

export function ApproveModal({ borrador, onConfirm, onCancel, isLoading }: ApproveModalProps) {
  const [aprobadoPor, setAprobadoPor] = useState('admin-system@fakemail.com')

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle size={18} className="text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-800">Aprobar borrador</h3>
              <p className="text-xs text-slate-500">El correo se enviará inmediatamente</p>
            </div>
          </div>
          <button
            onClick={onCancel}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Borrador summary */}
        <div className="bg-slate-50 rounded-lg p-3 mb-4 border border-slate-200">
          <p className="text-xs text-slate-500 mb-1">Destinatario</p>
          <p className="text-sm font-medium text-slate-800">{borrador.destinatario_email}</p>
          <p className="text-xs text-slate-500 mt-2 mb-1">Asunto</p>
          <p className="text-sm text-slate-700">{borrador.asunto}</p>
        </div>

        {/* Aprobado por */}
        <div className="mb-5">
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Aprobado por (email)
          </label>
          <input
            type="email"
            value={aprobadoPor}
            onChange={(e) => setAprobadoPor(e.target.value)}
            placeholder="tu@email.com"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
          />
        </div>

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={() => onConfirm(aprobadoPor)}
            disabled={!aprobadoPor || isLoading}
            className="flex-1 px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <CheckCircle size={15} />
            )}
            Aprobar y enviar
          </button>
        </div>
      </div>
    </div>
  )
}

interface RejectModalProps {
  borrador: BorradorCorreo
  onConfirm: (motivo: string) => void
  onCancel: () => void
  isLoading?: boolean
}

export function RejectModal({ borrador, onConfirm, onCancel, isLoading }: RejectModalProps) {
  const [motivo, setMotivo] = useState('')

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 bg-red-100 rounded-full flex items-center justify-center">
              <XCircle size={18} className="text-red-600" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-800">Rechazar borrador</h3>
              <p className="text-xs text-slate-500">Para: {borrador.destinatario_email}</p>
            </div>
          </div>
          <button
            onClick={onCancel}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <div className="mb-5">
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Motivo del rechazo
          </label>
          <textarea
            value={motivo}
            onChange={(e) => setMotivo(e.target.value)}
            placeholder="Describe por qué se rechaza este borrador..."
            rows={3}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
          />
        </div>

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={() => onConfirm(motivo)}
            disabled={!motivo || isLoading}
            className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <XCircle size={15} />
            )}
            Rechazar borrador
          </button>
        </div>
      </div>
    </div>
  )
}
