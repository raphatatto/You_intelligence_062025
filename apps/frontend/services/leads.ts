import useSWR from 'swr'
import type { Lead } from '@/app/types/lead'
import { CNAE_SEGMENTOS } from '@/utils/cnae'

const base = process.env.NEXT_PUBLIC_API_BASE ?? ''

// Fetcher SP
const fetcherSP = async (): Promise<Lead[]> => {
  const res = await fetch(`${base}/ucmt`)
  if (!res.ok) throw new Error('Erro ao carregar leads da API SP')

  const raw = await res.json()
  return raw.map((item: any) => ({
    id: item.COD_ID,
    dicMed: item.dic_med,
    ficMed: item.fic_med,
    cnae: item.CNAE,
    bairro: item.BRR,
    cep: item.CEP,
    estado: 'SP',
    distribuidora: String(item.DIST),
    codigoDistribuidora: String(item.DIST),
    segmento: CNAE_SEGMENTOS[item.CNAE] ?? 'Outro',
    descricao: item.DESCR
  }))
}

// Fetcher RJ
const fetcherRJ = async (): Promise<Lead[]> => {
  const res = await fetch(`${base}/ucmt/rj`)
  if (!res.ok) throw new Error('Erro ao carregar leads da API RJ')

  const raw = await res.json()
  return raw.map((item: any) => ({
    id: item.COD_ID,
    dicMed: item.dic_med,
    ficMed: item.fic_med,
    cnae: item.CNAE,
    bairro: item.BRR,
    cep: item.CEP,
    estado: 'RJ',
    distribuidora: String(item.DIST),
    codigoDistribuidora: String(item.DIST),
    segmento: CNAE_SEGMENTOS[item.CNAE] ?? 'Outro',
    descricao: item.DESCR
  }))
}

// Hook principal
export function useLeads() {
  const { data: sp, error: errorSP } = useSWR<Lead[]>('/ucmt', fetcherSP, {
    revalidateOnFocus: false,
    onErrorRetry: () => {},
  })

  const { data: rj, error: errorRJ } = useSWR<Lead[]>('/ucmt/rj', fetcherRJ, {
    revalidateOnFocus: false,
    onErrorRetry: () => {},
  })

  const leads = [...(sp ?? []), ...(rj ?? [])]
  const error = errorSP || errorRJ
  const isLoading = !sp || !rj

  return {
    leads,
    total: leads.length,
    isLoading,
    error,
  }
}
