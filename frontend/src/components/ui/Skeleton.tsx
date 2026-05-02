interface SkeletonProps {
  className?: string
}

export function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div
      className={`bg-slate-200 rounded animate-pulse ${className}`}
    />
  )
}

export function SolicitudCardSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Skeleton className="w-2 h-2 rounded-full" />
          <Skeleton className="h-5 w-20" />
          <Skeleton className="h-4 w-32" />
        </div>
        <Skeleton className="h-4 w-24" />
      </div>
      <Skeleton className="h-4 w-3/4 mb-2" />
      <Skeleton className="h-4 w-1/2" />
    </div>
  )
}

export function MetricCardSkeleton() {
  return (
    <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
      <Skeleton className="h-7 w-12 mb-1" />
      <Skeleton className="h-3 w-20" />
    </div>
  )
}
