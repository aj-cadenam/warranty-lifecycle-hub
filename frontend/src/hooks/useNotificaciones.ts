import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function useNotificaciones() {
  return useQuery({
    queryKey: ['notificaciones'],
    queryFn: api.getNotificaciones,
    refetchInterval: 30000,
    retry: 2,
  })
}
