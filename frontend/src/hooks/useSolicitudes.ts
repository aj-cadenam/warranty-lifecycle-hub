import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type { ChatRequest } from '../types'

export function useSolicitudes() {
  return useQuery({
    queryKey: ['solicitudes'],
    queryFn: api.getSolicitudes,
    refetchInterval: 30000,
    retry: 2,
  })
}

export function useActualizarEstado() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, estado }: { id: string; estado: string }) =>
      api.actualizarEstado(id, estado),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['solicitudes'] })
    },
  })
}

export function useCrearSolicitud() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.crearSolicitud,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['solicitudes'] })
    },
  })
}

export function useVerificarSemanal() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.verificarSemanal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['solicitudes'] })
      queryClient.invalidateQueries({ queryKey: ['borradores'] })
    },
  })
}

export function useProcesarDocumento() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.procesarDocumento,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['solicitudes'] })
    },
  })
}

export function useBuscarSimilares() {
  return useMutation({
    mutationFn: api.buscarSimilares,
  })
}

export function useChatAgente() {
  return useMutation({
    mutationFn: (payload: ChatRequest) => api.chatAgente(payload),
  })
}
