import { LayoutDashboard, Shield, Monitor, Mail, RefreshCw, Wifi, WifiOff, Bell } from 'lucide-react'
import type { NavSection } from '../../types'
import { MetricCardSkeleton } from '../ui/Skeleton'

interface NavItem {
  id: NavSection
  label: string
  icon: React.ComponentType<{ size?: number; className?: string }>
  badge?: number
}

interface LeftPanelProps {
  activeSection: NavSection
  onSectionChange: (section: NavSection) => void
  solicitudesCount: number
  borradorsPendingCount: number
  isLoading: boolean
  isApiConnected: boolean
}

export function LeftPanel({
  activeSection,
  onSectionChange,
  solicitudesCount,
  borradorsPendingCount,
  isLoading,
  isApiConnected,
}: LeftPanelProps) {
  const navItems: NavItem[] = [
    { id: 'dashboard',      label: 'Inicio',              icon: LayoutDashboard },
    { id: 'garantias',      label: 'Casos activos',        icon: Shield, badge: solicitudesCount },
    { id: 'equipos',        label: 'Equipos',              icon: Monitor },
    { id: 'borradores',     label: 'Correos para aprobar', icon: Mail, badge: borradorsPendingCount },
    { id: 'verificar',      label: 'Revisión semanal',     icon: RefreshCw },
    { id: 'notificaciones', label: 'Notificaciones',       icon: Bell },
  ]

  return (
    <div className="w-60 flex-shrink-0 bg-white border-r border-slate-200 flex flex-col h-full">
      {/* Logo / header */}
      <div className="px-4 py-4 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-brand-600 rounded flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-black tracking-widest">D</span>
          </div>
          <div>
            <h1 className="text-sm font-black text-slate-900 leading-tight tracking-tight uppercase">Datecsa</h1>
            <p className="text-[10px] font-semibold text-brand-600 tracking-widest uppercase leading-tight">Garantías</p>
          </div>
        </div>
      </div>

      {/* API connection status */}
      <div className="px-4 py-3 border-b border-slate-100">
        {isApiConnected ? (
          <div className="flex items-center gap-2 px-3 py-2 bg-green-50 rounded-lg border border-green-200">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse-dot" />
            <span className="text-xs text-green-700 font-medium">API Conectada</span>
            <Wifi size={12} className="text-green-600 ml-auto" />
          </div>
        ) : (
          <div className="flex items-center gap-2 px-3 py-2 bg-red-50 rounded-lg border border-red-200">
            <span className="w-2 h-2 bg-red-400 rounded-full" />
            <span className="text-xs text-red-700 font-medium">Sin conexión</span>
            <WifiOff size={12} className="text-red-500 ml-auto" />
          </div>
        )}
      </div>

      {/* Quick metrics */}
      <div className="px-4 py-3 border-b border-slate-100">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Métricas</p>
        <div className="grid grid-cols-2 gap-2">
          {isLoading ? (
            <>
              <MetricCardSkeleton />
              <MetricCardSkeleton />
            </>
          ) : (
            <>
              <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                <p className="text-xl font-bold text-brand-600">{solicitudesCount}</p>
                <p className="text-xs text-slate-500 leading-tight mt-0.5">Casos activos</p>
              </div>
              <div
                className={`rounded-lg p-3 border ${
                  borradorsPendingCount > 0
                    ? 'bg-amber-50 border-amber-200'
                    : 'bg-slate-50 border-slate-100'
                }`}
              >
                <p className={`text-xl font-bold ${borradorsPendingCount > 0 ? 'text-amber-700' : 'text-slate-800'}`}>
                  {borradorsPendingCount}
                </p>
                <p className={`text-xs leading-tight mt-0.5 ${borradorsPendingCount > 0 ? 'text-amber-600' : 'text-slate-500'}`}>
                  Correos pendientes
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-3 overflow-y-auto">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2 px-1">Navegación</p>
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive = activeSection === item.id
            return (
              <li key={item.id}>
                <button
                  onClick={() => onSectionChange(item.id)}
                  className={`
                    w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all
                    ${isActive
                      ? 'bg-brand-600 text-white shadow-sm'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-800'
                    }
                  `}
                >
                  <item.icon
                    size={16}
                    className={isActive ? 'text-white' : 'text-slate-400'}
                  />
                  <span className="flex-1 text-left">{item.label}</span>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span
                      className={`
                        text-xs font-semibold px-1.5 py-0.5 rounded-full
                        ${isActive ? 'bg-white/20 text-white' : 'bg-amber-100 text-amber-700'}
                      `}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* User footer */}
      <div className="px-4 py-3 border-t border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-brand-600 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-semibold">JC</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-800 truncate">Javier Cadena</p>
            <p className="text-xs text-slate-400">Admin</p>
          </div>
        </div>
      </div>
    </div>
  )
}
