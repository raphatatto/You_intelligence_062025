import useSWR from 'swr'
import type { Lead } from '@/app/types/lead'
import { CNAE_SEGMENTOS } from '@/utils/cnae'

const base = process.env.NEXT_PUBLIC_API_BASE ?? ''

// Fetcher SP

const fetcherTop300 = async (): Promise<Lead[]> => {
  const res = await fetch(`${base}/leads-geo`)
  if (!res.ok) throw new Error('Erro ao carregar os leads detalhados')

  const raw = await res.json()

  return raw.map((item: any) => {
    const cnae = item.cnae ?? item.CNAE
    return {
      id: String(item.cod_id ?? item.COD_ID ?? item.id ?? ''),
      ucId: String(item.uc_id ?? item.UC_ID ?? ''),
      descricao: item.descricao ?? item.DESCR ?? null,
      cnae,
      segmento: CNAE_SEGMENTOS[cnae] ?? item.segmento_desc ?? null,
      tipo: item.tipo ?? null,
      bairro: item.bairro ?? item.BRR ?? null,
      cep: item.cep ?? null,
      distribuidora: item.distribuidora_nome ?? item.DIST ?? null,
      municipio: item.municipio_nome ?? null,
      estado: item.uf ?? item.estado ?? null,
      latitude: item.latitude_final ?? item.latitude ?? null,
      longitude: item.longitude_final ?? item.longitude ?? null,
      potencia: item.pac ?? null,
      dicMed: item.media_dic ?? item.dic_med ?? null,
      ficMed: item.media_fic ?? item.fic_med ?? null,
      energiaMediaTotal: item.media_energia_total ?? null,
      demandaMediaContratada: item.media_demanda_contratada ?? null,
    }
  })
}

export function useLeads() {
  const { data, error } = useSWR<Lead[]>('/leads-geo', fetcherTop300, {
    revalidateOnFocus: false,
    onErrorRetry: () => {},
  })

  const leads = data ?? []
  const isLoading = !data

  console.log('[📊] Leads finais no front:', leads.length)

  return {
    leads,
    total: leads.length,
    isLoading,
    error,
  }
}

