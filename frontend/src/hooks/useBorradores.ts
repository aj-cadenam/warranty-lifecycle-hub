import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'

export function useBorradores() {
  return useQuery({
    queryKey: ['borradores'],
    queryFn: api.getBorradores,
    refetchInterval: 30000,
    retry: 2,
  })
}

export function useAprobarBorrador() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, aprobadoPor }: { id: string; aprobadoPor: string }) =>
      api.aprobarBorrador(id, aprobadoPor),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['borradores'] })
      queryClient.invalidateQueries({ queryKey: ['solicitudes'] })
    },
  })
}

export function useRechazarBorrador() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, motivo }: { id: string; motivo: string }) =>
      api.rechazarBorrador(id, motivo),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['borradores'] })
    },
  })
}

export function useEditarBorrador() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, cuerpo }: { id: string; cuerpo: string }) =>
      api.editarBorrador(id, cuerpo),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['borradores'] })
    },
  })
}
