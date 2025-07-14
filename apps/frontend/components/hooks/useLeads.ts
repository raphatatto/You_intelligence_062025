// hooks/useLeads.ts
import useSWR from 'swr'
import type { Lead } from '@/app/types/lead'
import { CNAE_SEGMENTOS } from '@/utils/cnae'

const base = process.env.NEXT_PUBLIC_API_BASE ?? ''

const fetcherLeads = async (): Promise<Lead[]> => {
  const res = await fetch(`${base}/v1/leads`)
  if (!res.ok) throw new Error('Erro ao buscar leads')

  const raw = await res.json()

  return raw.map((item: any) => ({
    id: item.cod_id,
    dicMed: item.media_dic,
    ficMed: item.media_fic,
    cnae: item.cnae,
    bairro: item.bairro,
    cep: item.cep,
    estado: item.municipio_uf,
    distribuidora: item.distribuidora,
    codigoDistribuidora: item.codigo_distribuidora,
    segmento: CNAE_SEGMENTOS[item.cnae] ?? 'Outro',
    descricao: item.descricao,
    tipo: item.classe_desc ?? 'N/A',
    latitude: item.latitude_final,
    longitude: item.longitude_final,
  }))
}

export function useLeads() {
  const { data, error } = useSWR<Lead[]>('/leads', fetcherLeads, {
    revalidateOnFocus: false,
    onErrorRetry: () => {},
  })

  const leads = data ?? []
  const isLoading = !data && !error

  return {
    leads,
    total: leads.length,
    isLoading,
    error,
  }
}
