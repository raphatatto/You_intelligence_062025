import useSWR from 'swr';
import type { Lead } from '@/app/types/lead';

const base = process.env.NEXT_PUBLIC_API_BASE ?? '';
const fetcher = (url: string) => fetch(base + url).then(r => r.json());

export const useLeads = (qs = '') =>
  useSWR<Lead[]>(
    `/api/leads${qs ? '?' + qs : ''}`,   // ex.: /api/leads?regiao=Sul
    fetcher,
    { refreshInterval: 60000 }          // refetch a cada 60 s (opcional)
  );
