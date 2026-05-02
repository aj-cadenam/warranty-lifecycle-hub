import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'

export function useEquipos() {
  return useQuery({
    queryKey: ['equipos'],
    queryFn: api.getEquipos,
    refetchInterval: 60000,
    retry: 2,
  })
}

export function useCrearEquipo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.crearEquipo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipos'] })
    },
  })
}
