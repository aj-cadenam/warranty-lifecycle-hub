import { useState, useEffect } from 'react'
import { Bot } from 'lucide-react'
import type { SolicitudGarantia, BorradorCorreo } from '../../types'
import { AgentChat } from '../agent/AgentChat'
import { api } from '../../api/client'

interface RightPanelProps {
  solicitudes: SolicitudGarantia[]
  borradores: BorradorCorreo[]
  onToast: (message: string, type?: 'success' | 'error' | 'info') => void
}

export function RightPanel({ solicitudes, borradores, onToast }: RightPanelProps) {
  const [llmProvider, setLlmProvider] = useState('...')
  useEffect(() => {
    api.getHealth().then(h => setLlmProvider(h.llm_provider)).catch(() => setLlmProvider('?'))
  }, [])
  const providerLabel = llmProvider === 'gemini' ? 'Gemini · Real' : llmProvider === '...' ? 'Gemini · ...' : 'Gemini · Mock mode'

  return (
    <div className="w-80 flex-shrink-0 bg-white border-l border-slate-200 flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-4 border-b border-slate-100 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-gradient-to-br from-brand-500 to-brand-700 rounded-lg flex items-center justify-center">
            <Bot size={18} className="text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-slate-800">Agente IA</span>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse-dot" />
                <span className="text-xs text-green-600 font-medium">Activo</span>
              </div>
            </div>
            <p className="text-xs text-slate-400">{providerLabel}</p>
          </div>
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 overflow-hidden">
        <AgentChat
          solicitudes={solicitudes}
          borradores={borradores}
          onToast={onToast}
        />
      </div>
    </div>
  )
}
