import { useState } from 'react'
import { Mail, CheckCircle, XCircle, Save, X, ChevronDown, ChevronUp, Edit3 } from 'lucide-react'
import type { BorradorCorreo } from '../../types'
import { BorradorBadge } from '../ui/Badge'
import { ApproveModal, RejectModal } from './ApprovalModal'
import { useAprobarBorrador, useRechazarBorrador, useEditarBorrador } from '../../hooks/useBorradores'

interface BorradorCardProps {
  borrador: BorradorCorreo
  onActionSuccess: (message: string, type?: 'success' | 'error') => void
}

export function BorradorCard({ borrador, onActionSuccess }: BorradorCardProps) {
  const [showApproveModal, setShowApproveModal] = useState(false)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [expanded, setExpanded] = useState(false)
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
      onActionSuccess('Correo enviado correctamente')
    } catch {
      onActionSuccess('Error al enviar el correo', 'error')
    }
  }

  const handleReject = async (motivo: string) => {
    try {
      await rechazarMutation.mutateAsync({ id: borrador.id, motivo })
      setShowRejectModal(false)
      onActionSuccess('Correo descartado')
    } catch {
      onActionSuccess('Error al descartar el correo', 'error')
    }
  }

  const handleSaveBody = async () => {
    try {
      await editarMutation.mutateAsync({ id: borrador.id, cuerpo: bodyText })
      setEditingBody(false)
      onActionSuccess('Contenido actualizado')
    } catch {
      onActionSuccess('Error al actualizar el contenido', 'error')
    }
  }

  return (
    <>
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        {/* Compact header — always visible */}
        <div className="px-4 py-3 flex items-center justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <Mail size={13} className="text-slate-400 flex-shrink-0" />
              <span className="text-sm font-medium text-slate-800 truncate">{borrador.destinatario_email}</span>
              {borrador.dias_sin_respuesta !== undefined && (
                <span className="text-xs text-orange-600 font-medium flex-shrink-0">
                  · {borrador.dias_sin_respuesta}d sin respuesta
                </span>
              )}
              <BorradorBadge estado={borrador.estado} />
            </div>
            <p className="text-xs text-slate-500 truncate mt-0.5 pl-5">{borrador.asunto}</p>
          </div>

          {isPending && (
            <div className="flex items-center gap-1.5 flex-shrink-0">
              <button
                onClick={() => setShowRejectModal(true)}
                disabled={isLoading}
                className="text-xs text-slate-500 hover:text-red-600 px-2 py-1 rounded transition-colors disabled:opacity-50"
              >
                Descartar
              </button>
              <button
                onClick={() => setShowApproveModal(true)}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-brand-600 text-white rounded-lg text-xs font-semibold hover:bg-brand-700 transition-colors disabled:opacity-50"
              >
                <CheckCircle size={13} />
                Enviar correo
              </button>
            </div>
          )}

          {(borrador.estado === 'aprobado' || borrador.estado === 'enviado') && borrador.aprobado_por && (
            <div className="flex items-center gap-1.5 text-xs text-slate-500 flex-shrink-0">
              <CheckCircle size={12} className="text-green-500" />
              <span>Enviado por <strong>{borrador.aprobado_por}</strong></span>
            </div>
          )}
        </div>

        {/* Expand toggle */}
        <button
          onClick={() => setExpanded(v => !v)}
          className="w-full flex items-center gap-1.5 px-4 py-2 border-t border-slate-100 text-xs text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors"
        >
          {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          {expanded ? 'Ocultar contenido del correo' : 'Ver contenido del correo'}
        </button>

        {/* Expandable body */}
        {expanded && (
          <div className="px-4 pb-4 border-t border-slate-50">
            <div className="flex items-center justify-between mt-3 mb-2">
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
                rows={6}
                className="w-full text-xs text-slate-700 bg-slate-50 border border-slate-200 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none leading-relaxed"
              />
            ) : (
              <div className="text-xs text-slate-700 leading-relaxed bg-slate-50 rounded-lg p-3 border border-slate-100 whitespace-pre-wrap">
                {borrador.cuerpo || 'Sin contenido'}
              </div>
            )}

            {borrador.solicitud_id && (
              <p className="text-xs text-slate-400 mt-2">
                Solicitud #{borrador.solicitud_id.slice(0, 8)}
              </p>
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
