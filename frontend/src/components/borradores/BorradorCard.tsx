import { useState } from 'react'
import { Mail, CheckCircle, XCircle, Clock, Edit3, Save, X } from 'lucide-react'
import type { BorradorCorreo } from '../../types'
import { BorradorBadge } from '../ui/Badge'
import { ApproveModal, RejectModal } from './ApprovalModal'
import { useAprobarBorrador, useRechazarBorrador, useEditarBorrador } from '../../hooks/useBorradores'

function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
  } catch {
    return dateStr
  }
}

interface BorradorCardProps {
  borrador: BorradorCorreo
  onActionSuccess: (message: string, type?: 'success' | 'error') => void
}

export function BorradorCard({ borrador, onActionSuccess }: BorradorCardProps) {
  const [showApproveModal, setShowApproveModal] = useState(false)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [editingBody, setEditingBody] = useState(false)
  const [bodyText, setBodyText] = useState(borrador.cuerpo)

  const aprobarMutation = useAprobarBorrador()
  const rechazarMutation = useRechazarBorrador()
  const editarMutation = useEditarBorrador()

  const isPending = borrador.estado === 'pendiente_aprobacion'
  const isLoading = aprobarMutation.isPending || rechazarMutation.isPending

  const handleApprove = async (aprobadoPor: string) => {
    try {
      await aprobarMutation.mutateAsync({ id: borrador.id, aprobadoPor })
      setShowApproveModal(false)
      onActionSuccess('Borrador aprobado y correo enviado correctamente')
    } catch (err) {
      onActionSuccess('Error al aprobar el borrador', 'error')
    }
  }

  const handleReject = async (motivo: string) => {
    try {
      await rechazarMutation.mutateAsync({ id: borrador.id, motivo })
      setShowRejectModal(false)
      onActionSuccess('Borrador rechazado')
    } catch (err) {
      onActionSuccess('Error al rechazar el borrador', 'error')
    }
  }

  const handleSaveBody = async () => {
    try {
      await editarMutation.mutateAsync({ id: borrador.id, cuerpo: bodyText })
      setEditingBody(false)
      onActionSuccess('Borrador actualizado')
    } catch (err) {
      onActionSuccess('Error al actualizar el borrador', 'error')
    }
  }

  return (
    <>
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        {/* Header */}
        <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-brand-50 rounded-full flex items-center justify-center">
              <Mail size={15} className="text-brand-600" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-slate-800">
                  Borrador #{borrador.id.slice(0, 8)}
                </span>
                <BorradorBadge estado={borrador.estado} />
              </div>
              <p className="text-xs text-slate-500">{formatDate(borrador.created_at)}</p>
            </div>
          </div>
          {isPending && (
            <div className="flex items-center gap-1.5 text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded-full border border-amber-200">
              <Clock size={12} />
              Requiere aprobación
            </div>
          )}
        </div>

        {/* Email metadata */}
        <div className="px-4 py-3 bg-slate-50/60 border-b border-slate-100 space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-slate-500 w-16">Para:</span>
            <span className="text-xs text-slate-700 font-medium">{borrador.destinatario_email}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-slate-500 w-16">Asunto:</span>
            <span className="text-xs text-slate-700">{borrador.asunto}</span>
          </div>
          {borrador.solicitud_id && (
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-slate-500 w-16">Solicitud:</span>
              <span className="text-xs text-slate-500">#{borrador.solicitud_id.slice(0, 8)}</span>
              {borrador.dias_sin_respuesta !== undefined && (
                <span className="text-xs text-orange-600 font-medium">
                  · {borrador.dias_sin_respuesta} días sin respuesta
                </span>
              )}
            </div>
          )}
        </div>

        {/* Body */}
        <div className="px-4 py-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">Contenido</span>
            {isPending && !editingBody && (
              <button
                onClick={() => setEditingBody(true)}
                className="flex items-center gap-1 text-xs text-brand-600 hover:text-brand-700 transition-colors"
              >
                <Edit3 size={12} />
                Editar
              </button>
            )}
            {editingBody && (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => { setEditingBody(false); setBodyText(borrador.cuerpo) }}
                  className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700 transition-colors"
                >
                  <X size={12} />
                  Cancelar
                </button>
                <button
                  onClick={handleSaveBody}
                  disabled={editarMutation.isPending}
                  className="flex items-center gap-1 text-xs text-green-600 hover:text-green-700 transition-colors"
                >
                  <Save size={12} />
                  Guardar
                </button>
              </div>
            )}
          </div>

          {editingBody ? (
            <textarea
              value={bodyText}
              onChange={(e) => setBodyText(e.target.value)}
              rows={5}
              className="w-full text-xs text-slate-700 bg-slate-50 border border-slate-200 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none leading-relaxed"
            />
          ) : (
            <div className="text-xs text-slate-700 leading-relaxed bg-slate-50 rounded-lg p-3 border border-slate-100 line-clamp-4">
              {borrador.cuerpo || 'Sin contenido'}
            </div>
          )}
        </div>

        {/* Actions */}
        {isPending && (
          <div className="px-4 py-3 border-t border-slate-100 flex items-center justify-end gap-2">
            <button
              onClick={() => setShowRejectModal(true)}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 border border-red-200 text-red-600 rounded-lg text-xs font-medium hover:bg-red-50 transition-colors disabled:opacity-50"
            >
              <XCircle size={14} />
              Rechazar
            </button>
            <button
              onClick={() => setShowApproveModal(true)}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-brand-600 text-white rounded-lg text-xs font-medium hover:bg-brand-700 transition-colors disabled:opacity-50"
            >
              <CheckCircle size={14} />
              Aprobar
            </button>
          </div>
        )}

        {/* Approved/Sent state */}
        {(borrador.estado === 'aprobado' || borrador.estado === 'enviado') && borrador.aprobado_por && (
          <div className="px-4 py-3 border-t border-slate-100 flex items-center gap-2 text-xs text-slate-500">
            <CheckCircle size={13} className="text-green-500" />
            <span>Aprobado por <strong>{borrador.aprobado_por}</strong></span>
            {borrador.fecha_aprobacion && (
              <span>· {formatDate(borrador.fecha_aprobacion)}</span>
            )}
          </div>
        )}
      </div>

      {showApproveModal && (
        <ApproveModal
          borrador={borrador}
          onConfirm={handleApprove}
          onCancel={() => setShowApproveModal(false)}
          isLoading={aprobarMutation.isPending}
        />
      )}

      {showRejectModal && (
        <RejectModal
          borrador={borrador}
          onConfirm={handleReject}
          onCancel={() => setShowRejectModal(false)}
          isLoading={rechazarMutation.isPending}
        />
      )}
    </>
  )
}
