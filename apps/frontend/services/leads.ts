import useSWR from 'swr';
import type { Lead, LeadList } from '@/app/types/lead';

// pega da env e cai no '' se não estiver definido
const base = process.env.NEXT_PUBLIC_API_BASE ?? '';

const fetcher = (url: string) =>
  fetch(`${base}${url}`, {
    headers: {
      // se sua API exigir JWT, descomente e implemente getToken()
      // Authorization: `Bearer ${getToken()}`
    },
  }).then((r) => {
    if (!r.ok) throw new Error('Erro ao carregar leads da API');
    return r.json() as Promise<LeadList>;
  });

export function useLeads() {
  const { data, error, isValidating } = useSWR<LeadList>('/v1/leads', fetcher, {
    revalidateOnFocus: false,
    onErrorRetry: () => {}, // evita loop infinito
  });

  return {
    leads: data?.items ?? [],    // array puro para uso no front
    total: data?.total ?? 0,
    isLoading: isValidating,
    error,
  };
}
