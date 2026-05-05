import { useState, useRef, useEffect, type ReactNode } from 'react'
import {
  Inbox,
  Mail,
  Paperclip,
  ArrowRight,
  Sparkles,
  Send,
  Zap,
  CheckCircle2,
} from 'lucide-react'
import { api } from '../../api/client'
import type {
  SolicitudGarantia,
  InboxPreview,
  PipelineResult,
  PipelineEmailResult,
} from '../../types'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const TIPO_LABEL: Record<string, string> = {
  acta_entrega: 'Acta de entrega',
  actualizacion_proveedor: 'Actualización proveedor',
  confirmacion_despacho: 'Confirmación despacho',
  confirmacion_devolucion: 'Devolución equipo',
  consulta_cliente: 'Consulta cliente',
  otro: 'Otro',
}

const TIPO_COLOR: Record<string, string> = {
  acta_entrega: 'bg-amber-100 text-amber-800',
  actualizacion_proveedor: 'bg-blue-100 text-blue-800',
  confirmacion_despacho: 'bg-purple-100 text-purple-800',
  confirmacion_devolucion: 'bg-green-100 text-green-800',
  consulta_cliente: 'bg-slate-100 text-slate-700',
  otro: 'bg-slate-100 text-slate-500',
}

const ACCION_LABEL: Record<string, string> = {
  solicitud_creada_desde_correo: 'Solicitud creada',
  solicitud_creada_desde_pdf: 'Solicitud desde PDF',
  estado_actualizado: 'Estado actualizado',
  consulta_registrada: 'Consulta registrada',
  ignorado: 'Ignorado',
  sin_serial_identificado: 'Sin serial identificado',
  equipo_sin_garantia_vigente: 'Sin garantía vigente',
  solicitud_activa_no_encontrada: 'Solicitud no encontrada',
}

const DEST_LABEL: Record<string, string> = {
  responsable: 'Responsable',
  bodega: 'Bodega',
  despacho: 'Despacho',
  recepcion: 'Recepción',
  proveedor: 'Proveedor',
  cliente: 'Cliente',
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type Phase = 'idle' | 'loading_preview' | 'preview' | 'running' | 'done'
type EmailPhase = 'pending' | 'classifying' | 'processing' | 'orchestrating' | 'done'

interface EmailAnimState {
  phase: EmailPhase
  result?: PipelineEmailResult
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StepBadge({ icon, label }: { icon: ReactNode; label: string }) {
  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="w-9 h-9 rounded-full bg-brand-50 border border-brand-200 flex items-center justify-center text-brand-600">
        {icon}
      </div>
      <span className="text-xs text-slate-500 text-center max-w-[80px] leading-tight">{label}</span>
    </div>
  )
}

interface EmailProcessingCardProps {
  asunto: string
  remitente: string
  state: EmailAnimState
}

function EmailProcessingCard({ asunto, remitente, state }: EmailProcessingCardProps) {
  const { phase, result } = state

  const isPending = phase === 'pending'

  // Stage completion flags
  const stage1Done = ['processing', 'orchestrating', 'done'].includes(phase)
  const stage2Done = ['orchestrating', 'done'].includes(phase)
  const stage3Done = phase === 'done'

  // Animating (pulsing) flags
  const stage1Animating = phase === 'classifying'
  const stage2Animating = phase === 'processing'
  const stage3Animating = phase === 'orchestrating'

  function StageIcon({
    icon,
    label,
    done,
    animating,
  }: {
    icon: ReactNode
    label: string
    done: boolean
    animating: boolean
  }) {
    return (
      <div className="flex items-center gap-1.5">
        {done ? (
          <CheckCircle2 size={14} className="text-green-500 flex-shrink-0" />
        ) : (
          <span
            className={`flex-shrink-0 ${
              animating ? 'animate-pulse text-brand-500' : 'text-slate-300'
            }`}
          >
            {icon}
          </span>
        )}
        <span
          className={`text-xs ${
            done
              ? 'text-green-700 font-medium'
              : animating
              ? 'text-brand-600 font-medium'
              : 'text-slate-400'
          }`}
        >
          {label}
        </span>
      </div>
    )
  }

  return (
    <div
      className={`p-3 bg-white rounded-lg border border-slate-200 transition-opacity duration-300 ${
        isPending ? 'opacity-50' : 'opacity-100'
      }`}
    >
      {/* Email header */}
      <div className="flex items-start gap-3 mb-2">
        <Mail size={14} className="text-slate-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-slate-800 truncate">{asunto}</p>
          <p className="text-xs text-slate-500">{remitente}</p>
        </div>
      </div>

      {/* Pipeline stages */}
      <div className="flex items-center gap-4 pl-5">
        <StageIcon
          icon={<Sparkles size={14} />}
          label="Clasificando"
          done={stage1Done}
          animating={stage1Animating}
        />
        <StageIcon
          icon={<Zap size={14} />}
          label="Procesando"
          done={stage2Done}
          animating={stage2Animating}
        />
        <StageIcon
          icon={<Send size={14} />}
          label="Orquestando"
          done={stage3Done}
          animating={stage3Animating}
        />
      </div>

      {/* Result details when done */}
      {phase === 'done' && result && (
        <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap gap-2">
          {result.tipo && (
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                TIPO_COLOR[result.tipo] ?? 'bg-slate-100 text-slate-500'
              }`}
            >
              {TIPO_LABEL[result.tipo] ?? result.tipo}
            </span>
          )}
          {result.accion_tomada && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-medium">
              {ACCION_LABEL[result.accion_tomada] ?? result.accion_tomada}
            </span>
          )}
          {result.destinatarios.map(d => (
            <span key={d} className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
              {DEST_LABEL[d] ?? d}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface PipelineRunnerProps {
  solicitudes: SolicitudGarantia[]
  onNavigateToBorradores: () => void
  onToast: (msg: string, type?: 'success' | 'error' | 'info') => void
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function PipelineRunner({
  solicitudes,
  onNavigateToBorradores,
  onToast,
}: PipelineRunnerProps) {
  const [phase, setPhase] = useState<Phase>('idle')
  const [preview, setPreview] = useState<InboxPreview | null>(null)
  const [result, setResult] = useState<PipelineResult | null>(null)
  const [emailStates, setEmailStates] = useState<EmailAnimState[]>([])

  const timeoutRefs = useRef<ReturnType<typeof setTimeout>[]>([])

  // Clear all pending timeouts
  function clearAllTimeouts() {
    timeoutRefs.current.forEach(id => clearTimeout(id))
    timeoutRefs.current = []
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearAllTimeouts()
    }
  }, [])

  const casosConProveedor = solicitudes.filter(s =>
    ['despachada', 'en_reparacion'].includes(s.estado)
  ).length

  // Derived counts
  const doneCount = emailStates.filter(s => s.phase === 'done').length
  const totalBorradores =
    result?.detalle.reduce((sum, r) => sum + r.borradores_generados, 0) ?? 0

  // -------------------------------------------------------------------------
  // Handlers
  // -------------------------------------------------------------------------

  async function handlePreview() {
    setPhase('loading_preview')
    try {
      const data = await api.inboxPreview()
      setPreview(data)
      setEmailStates(Array.from({ length: data.total }, () => ({ phase: 'pending' as EmailPhase })))
      setPhase('preview')
    } catch {
      onToast('Error al obtener bandeja', 'error')
      setPhase('idle')
    }
  }

  async function handleRun() {
    setPhase('running')
    try {
      const pipelineResult = await api.procesarCorreos()
      setResult(pipelineResult)
      const count = pipelineResult.detalle.length
      setEmailStates(Array.from({ length: count }, () => ({ phase: 'pending' as EmailPhase })))

      pipelineResult.detalle.forEach((emailResult, i) => {
        const addTimeout = (fn: () => void, delay: number) => {
          const id = setTimeout(fn, delay)
          timeoutRefs.current.push(id)
        }

        addTimeout(() => {
          setEmailStates(prev =>
            prev.map((s, j) => (j === i ? { ...s, phase: 'classifying' } : s))
          )
        }, i * 1200)

        addTimeout(() => {
          setEmailStates(prev =>
            prev.map((s, j) => (j === i ? { ...s, phase: 'processing' } : s))
          )
        }, i * 1200 + 400)

        addTimeout(() => {
          setEmailStates(prev =>
            prev.map((s, j) => (j === i ? { ...s, phase: 'orchestrating' } : s))
          )
        }, i * 1200 + 800)

        addTimeout(() => {
          setEmailStates(prev =>
            prev.map((s, j) =>
              j === i ? { phase: 'done', result: emailResult } : s
            )
          )
        }, i * 1200 + 1200)
      })

      const doneDelay = count * 1200
      const finalId = setTimeout(() => {
        setPhase('done')
      }, doneDelay)
      timeoutRefs.current.push(finalId)
    } catch {
      onToast('Error al ejecutar el pipeline', 'error')
      setPhase('preview')
    }
  }

  function reset() {
    clearAllTimeouts()
    setPhase('idle')
    setPreview(null)
    setResult(null)
    setEmailStates([])
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  if (phase === 'idle') {
    return (
      <div className="max-w-lg mx-auto text-center py-12">
        <div className="w-16 h-16 bg-brand-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Inbox size={28} className="text-brand-600" />
        </div>
        <h3 className="text-lg font-semibold text-slate-800 mb-2">
          Flujo completo del pipeline
        </h3>
        <p className="text-slate-500 text-sm mb-6 leading-relaxed">
          Simula el flujo completo: el agente revisa la bandeja, clasifica cada correo,
          actualiza trazabilidad y genera borradores para los destinatarios correctos.
        </p>

        {/* 3-step pipeline preview */}
        <div className="flex items-center justify-center gap-4 my-6">
          <StepBadge icon={<Mail size={14} />} label="Detectar correos" />
          <ArrowRight size={14} className="text-slate-300" />
          <StepBadge icon={<Sparkles size={14} />} label="Clasificar & procesar" />
          <ArrowRight size={14} className="text-slate-300" />
          <StepBadge icon={<Send size={14} />} label="Generar borradores" />
        </div>

        {/* Stats line */}
        <p className="text-xs text-slate-400 mb-6">
          {casosConProveedor} casos activos con el proveedor
        </p>

        <button
          onClick={handlePreview}
          className="inline-flex items-center gap-2 px-6 py-3 bg-brand-600 text-white rounded-lg font-medium hover:bg-brand-700 transition-colors"
        >
          <Inbox size={16} />
          Ver bandeja y ejecutar
        </button>
      </div>
    )
  }

  if (phase === 'loading_preview') {
    return (
      <div className="max-w-lg mx-auto text-center py-12">
        <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
          <Inbox size={28} className="text-slate-400" />
        </div>
        <p className="text-slate-500 text-sm">Consultando bandeja de entrada...</p>
      </div>
    )
  }

  if (phase === 'preview') {
    return (
      <div className="max-w-2xl mx-auto py-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-slate-800">
            {preview!.total} correos en la bandeja
          </h3>
          {preview!.es_mock && (
            <span className="text-xs text-amber-600 bg-amber-50 border border-amber-200 px-2 py-1 rounded">
              Bandeja simulada
            </span>
          )}
        </div>

        <div className="space-y-2">
          {preview!.correos.map(c => (
            <div
              key={c.uid}
              className="flex items-center gap-3 p-3 bg-white rounded-lg border border-slate-200"
            >
              <Mail size={14} className="text-slate-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-800 truncate">{c.asunto}</p>
                <p className="text-xs text-slate-500">{c.remitente}</p>
              </div>
              {c.tiene_adjuntos && (
                <Paperclip size={12} className="text-slate-400 flex-shrink-0" />
              )}
            </div>
          ))}
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={() => setPhase('idle')}
            className="px-4 py-2 text-slate-600 text-sm font-medium hover:text-slate-800 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleRun}
            className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-brand-600 text-white rounded-lg font-medium hover:bg-brand-700 transition-colors"
          >
            <Zap size={16} />
            Ejecutar pipeline
          </button>
        </div>
      </div>
    )
  }

  // phase === 'running' || phase === 'done'
  return (
    <div className="max-w-2xl mx-auto py-6">
      {/* Progress bar */}
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden mb-6">
        <div
          className="h-full bg-brand-500 transition-all duration-500"
          style={{ width: `${(doneCount / (emailStates.length || 1)) * 100}%` }}
        />
      </div>

      {/* Email cards */}
      <div className="space-y-3">
        {emailStates.map((es, i) => (
          <EmailProcessingCard
            key={i}
            asunto={preview!.correos[i]?.asunto ?? ''}
            remitente={preview!.correos[i]?.remitente ?? ''}
            state={es}
          />
        ))}
      </div>

      {/* Done summary */}
      {phase === 'done' && result && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm font-medium text-green-800 mb-3">
            {result.procesados} correos procesados
            {totalBorradores > 0 && ` · ${totalBorradores} borradores generados`}
          </p>
          <div className="flex gap-3">
            {totalBorradores > 0 && (
              <button
                onClick={onNavigateToBorradores}
                className="flex items-center gap-1.5 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
              >
                Ver correos para aprobar
                <ArrowRight size={14} />
              </button>
            )}
            <button
              onClick={reset}
              className="px-4 py-2 text-slate-600 text-sm font-medium hover:text-slate-800 transition-colors"
            >
              Ejecutar de nuevo
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
