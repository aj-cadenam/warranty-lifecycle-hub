import { useState } from 'react'
import type { NavSection } from '../types'
import { LeftPanel } from '../components/layout/LeftPanel'
import { CenterPanel } from '../components/layout/CenterPanel'
import { FloatingAgentButton } from '../components/agent/FloatingAgentButton'
import { ToastContainer, useToast } from '../components/ui/Toast'
import { useSolicitudes } from '../hooks/useSolicitudes'
import { useBorradores } from '../hooks/useBorradores'
import { useEquipos } from '../hooks/useEquipos'
import { useNotificaciones } from '../hooks/useNotificaciones'

export function Dashboard() {
  const [activeSection, setActiveSection] = useState<NavSection>('dashboard')
  const { toasts, addToast, dismissToast } = useToast()

  const {
    data: solicitudes = [],
    isLoading: isLoadingSolicitudes,
    isError: isSolicitudesError,
  } = useSolicitudes()

  const {
    data: borradores = [],
    isLoading: isLoadingBorradores,
  } = useBorradores()

  const {
    data: equipos = [],
    isLoading: isLoadingEquipos,
  } = useEquipos()

  const {
    data: notificaciones = [],
    isLoading: isLoadingNotificaciones,
  } = useNotificaciones()

  const activasSolicitudes = solicitudes.filter((s) => s.estado !== 'cerrada')
  const borradorsPendingCount = borradores.filter((b) => b.estado === 'pendiente_aprobacion').length
  const isApiConnected = !isSolicitudesError

  const handleToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    addToast(message, type)
  }

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Left Panel */}
      <LeftPanel
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        solicitudesCount={activasSolicitudes.length}
        borradorsPendingCount={borradorsPendingCount}
        isLoading={isLoadingSolicitudes || isLoadingBorradores}
        isApiConnected={isApiConnected}
      />

      {/* Center Panel */}
      <CenterPanel
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        solicitudes={solicitudes}
        borradores={borradores}
        equipos={equipos}
        notificaciones={notificaciones}
        isLoadingSolicitudes={isLoadingSolicitudes}
        isLoadingBorradores={isLoadingBorradores}
        isLoadingEquipos={isLoadingEquipos}
        isLoadingNotificaciones={isLoadingNotificaciones}
        onToast={handleToast}
      />

      {/* Floating AI agent button */}
      <FloatingAgentButton
        solicitudes={solicitudes}
        borradores={borradores}
        onToast={handleToast}
      />

      {/* Toast notifications */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  )
}
