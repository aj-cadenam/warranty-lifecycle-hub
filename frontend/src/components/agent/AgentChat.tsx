import { useState, useRef, useEffect } from 'react'
import { Send, Bot } from 'lucide-react'
import type { ChatMessage, SolicitudGarantia, BorradorCorreo, BuscarResultado } from '../../types'
import { useVerificarSemanal, useBuscarSimilares, useChatAgente } from '../../hooks/useSolicitudes'

const SUGGESTED_PROMPTS = [
  '¿Cuál es el estado actual?',
  '¿Hay borradores pendientes?',
  'Buscar casos similares',
  'Verificar garantías',
]

function formatBuscarResults(query: string, resultados: BuscarResultado[]): string {
  if (resultados.length === 0) {
    return `No encontré casos similares para "${query}". Intenta con otros términos como la marca, modelo o descripción de la falla.`
  }
  const lines = [
    `Encontré ${resultados.length} caso${resultados.length > 1 ? 's' : ''} similar${resultados.length > 1 ? 'es' : ''} para "${query}":`,
    '',
    ...resultados.map((s, i) => {
      const similitud = Math.round(s.similitud * 100)
      return `${i + 1}. ${s.equipo_id}\n   ${s.descripcion_falla?.slice(0, 80) ?? '—'}\n   Estado: ${s.estado.replace('_', ' ')} · ${s.fecha_reporte} · ${similitud}% similitud`
    }),
  ]
  return lines.join('\n')
}

interface AgentChatProps {
  solicitudes: SolicitudGarantia[]
  borradores: BorradorCorreo[]
  onToast: (message: string, type?: 'success' | 'error' | 'info') => void
}

export function AgentChat({ solicitudes, borradores, onToast }: AgentChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const verificarMutation = useVerificarSemanal()
  const buscarMutation = useBuscarSimilares()
  const chatMutation = useChatAgente()
  const hasInitialized = useRef(false)
  const isThinking = verificarMutation.isPending || buscarMutation.isPending || chatMutation.isPending

  useEffect(() => {
    if (!hasInitialized.current) {
      hasInitialized.current = true
      const activasCount = solicitudes.filter((s) => s.estado !== 'cerrada').length
      const pendientesCount = borradores.filter((b) => b.estado === 'pendiente_aprobacion').length
      setTimeout(() => {
        setMessages([{
          id: 'init-1',
          role: 'agent',
          content: `Hola Javier. Tengo ${activasCount} solicitud${activasCount !== 1 ? 'es' : ''} activa${activasCount !== 1 ? 's' : ''} y ${pendientesCount} borrador${pendientesCount !== 1 ? 'es' : ''} pendiente${pendientesCount !== 1 ? 's' : ''} de aprobación. ¿En qué te puedo ayudar?`,
          timestamp: new Date(),
        }])
      }, 500)
    }
  }, [solicitudes, borradores])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const pushAgentMsg = (content: string) => {
    setMessages((prev) => [...prev, {
      id: `msg-${Date.now()}-agent`,
      role: 'agent',
      content,
      timestamp: new Date(),
    }])
  }

  const sendMessage = async (text: string) => {
    if (!text.trim()) return

    setMessages((prev) => [...prev, {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date(),
    }])
    setInput('')

    const lower = text.toLowerCase()

    // Shortcut: semantic search button goes directly to backend without LLM round-trip
    const isBuscar =
      lower.startsWith('buscar ') ||
      lower.startsWith('busca ') ||
      lower.includes('casos similares') ||
      lower.includes('similar a') ||
      lower === 'buscar casos similares'

    if (isBuscar) {
      const query = text
        .replace(/^buscar?\s+casos?\s+similares\s*(a|de)?\s*/i, '')
        .replace(/^buscar?\s+/i, '')
        .replace(/casos?\s+similares\s*(a|de)?\s*/i, '')
        .trim() || text
      try {
        const result = await buscarMutation.mutateAsync(query)
        pushAgentMsg(formatBuscarResults(query, result.resultados))
      } catch {
        pushAgentMsg('No pude conectarme con el motor de búsqueda semántica. ¿El backend está corriendo?')
      }
      return
    }

    // All other input goes to real LLM
    const activasCount = solicitudes.filter((s) => s.estado !== 'cerrada').length
    const pendientesCount = borradores.filter((b) => b.estado === 'pendiente_aprobacion').length
    const equiposActivos = solicitudes
      .filter((s) => s.estado !== 'cerrada')
      .slice(0, 5)
      .map((s) => s.equipo_id)

    try {
      const result = await chatMutation.mutateAsync({
        mensaje: text,
        contexto: {
          solicitudes_activas: activasCount,
          borradores_pendientes: pendientesCount,
          equipos_activos: equiposActivos,
        },
      })

      pushAgentMsg(result.respuesta)

      // LLM may also request a side-effect action
      if (result.accion === 'buscar_similares' && result.query_busqueda) {
        try {
          const buscarResult = await buscarMutation.mutateAsync(result.query_busqueda)
          pushAgentMsg(formatBuscarResults(result.query_busqueda, buscarResult.resultados))
        } catch {
          pushAgentMsg('No pude ejecutar la búsqueda semántica.')
        }
      } else if (result.accion === 'verificar_semanal') {
        try {
          const vResult = await verificarMutation.mutateAsync()
          pushAgentMsg(
            `Verificación completada: ${vResult.solicitudes_verificadas} solicitudes verificadas, ${vResult.borradores_generados} borradores generados.`
          )
          onToast('Verificación semanal completada', 'success')
        } catch {
          pushAgentMsg('No pude ejecutar la verificación semanal.')
        }
      }
    } catch {
      pushAgentMsg('No pude conectarme con el agente. ¿El backend está corriendo en http://localhost:8000?')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-slate-400">
              <Bot size={32} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">Iniciando agente...</p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} gap-2`}>
            {msg.role === 'agent' && (
              <div className="w-7 h-7 rounded-full bg-brand-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Bot size={14} className="text-white" />
              </div>
            )}
            <div className={`
              max-w-[85%] px-3 py-2 rounded-xl text-sm leading-relaxed whitespace-pre-line
              ${msg.role === 'user'
                ? 'bg-brand-600 text-white rounded-br-none'
                : 'bg-slate-100 text-slate-800 rounded-bl-none'
              }
            `}>
              {msg.content}
            </div>
          </div>
        ))}

        {isThinking && (
          <div className="flex justify-start gap-2">
            <div className="w-7 h-7 rounded-full bg-brand-600 flex items-center justify-center flex-shrink-0">
              <Bot size={14} className="text-white" />
            </div>
            <div className="bg-slate-100 px-3 py-2 rounded-xl rounded-bl-none">
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested prompts */}
      <div className="px-4 pb-2">
        <div className="flex flex-wrap gap-1.5">
          {SUGGESTED_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              onClick={() => sendMessage(prompt)}
              disabled={isThinking}
              className="text-xs px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-full border border-slate-200 transition-colors disabled:opacity-50"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="px-4 pb-4">
        <div className="flex gap-2 bg-slate-100 rounded-xl p-1.5 border border-slate-200">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Pregunta al agente..."
            className="flex-1 bg-transparent px-2 py-1 text-sm text-slate-800 placeholder-slate-400 focus:outline-none"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || isThinking}
            className="w-8 h-8 bg-brand-600 text-white rounded-lg flex items-center justify-center hover:bg-brand-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0"
          >
            <Send size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}
