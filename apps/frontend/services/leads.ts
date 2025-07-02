import useSWR from 'swr'
import type { Lead } from '@/app/types/lead'
import { CNAE_SEGMENTOS } from '@/utils/cnae'
const base = process.env.NEXT_PUBLIC_API_BASE ?? ''

const fetcher = async (url: string): Promise<Lead[]> => {
  const res = await fetch(`${base}${url}`);
  if (!res.ok) throw new Error('Erro ao carregar leads da API');
  const raw = await res.json();
    return raw.map((item: any) => ({
    id: item.COD_ID,
    dicMed: item.dic_med,
    ficMed: item.fic_med,
    cnae: item.CNAE,
    bairro: item.BRR,
    cep: item.CEP,
    estado: 'SP',
    distribuidora: String(item.DIST),
    segmento: CNAE_SEGMENTOS[item.CNAE] ?? 'Outro',
  }));
};

export function useLeads() {
  const { data, error, isValidating } = useSWR<Lead[]>('/ucmt', fetcher, {
    revalidateOnFocus: false,
    onErrorRetry: () => {},
  })

  return {
    leads: data ?? [],
    total: data?.length ?? 0,
    isLoading: isValidating,
    error,
  }
}
