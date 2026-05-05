import { useState } from 'react'
import { Sparkles, X } from 'lucide-react'
import { AgentChat } from './AgentChat'
import type { SolicitudGarantia, BorradorCorreo } from '../../types'

interface FloatingAgentButtonProps {
  solicitudes: SolicitudGarantia[]
  borradores: BorradorCorreo[]
  onToast: (message: string, type?: 'success' | 'error' | 'info') => void
}

export function FloatingAgentButton({ solicitudes, borradores, onToast }: FloatingAgentButtonProps) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <button
        onClick={() => setOpen(v => !v)}
        className={`fixed bottom-6 right-6 z-50 w-12 h-12 rounded-full shadow-lg flex items-center justify-center transition-all ${
          open ? 'bg-slate-700 hover:bg-slate-800' : 'bg-brand-600 hover:bg-brand-700'
        }`}
        title="Agente IA"
      >
        {open
          ? <X size={18} className="text-white" />
          : <Sparkles size={18} className="text-white" />
        }
      </button>

      {open && (
        <div
          className="fixed z-50 w-80 bg-white rounded-xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden"
          style={{ bottom: '80px', right: '24px', height: '480px' }}
        >
          <div className="px-4 py-3 border-b border-slate-100 flex-shrink-0 bg-gradient-to-r from-brand-600 to-brand-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles size={14} className="text-white" />
                <span className="text-sm font-semibold text-white">Agente IA</span>
                <span className="flex items-center gap-1 ml-1">
                  <span className="w-1.5 h-1.5 bg-green-300 rounded-full animate-pulse-dot" />
                  <span className="text-xs text-white/70">Activo</span>
                </span>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="text-white/70 hover:text-white transition-colors w-6 h-6 flex items-center justify-center rounded"
              >
                <X size={14} />
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-hidden">
            <AgentChat solicitudes={solicitudes} borradores={borradores} onToast={onToast} />
          </div>
        </div>
      )}
    </>
  )
}
