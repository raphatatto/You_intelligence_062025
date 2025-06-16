// services/leads.ts
import useSWR from 'swr';
import type { Lead } from '@/app/types/lead';
import { leadsMock } from '@/app/data/leads';

const base = process.env.NEXT_PUBLIC_API_BASE ?? '';
const fetcher = (url:string) => fetch(base + url).then(r => r.json());

export const useLeads = (qs = '') =>
  useSWR<Lead[]>(
    `/api/leads${qs ? '?' + qs : ''}`,
    fetcher,
    {
      /* 👇 enquanto o backend não existir, pinta o mapa com o mock */
      fallbackData: leadsMock,
      /* quando a rota real der 200, SWR substituirá automaticamente */
      refreshInterval: 60000,      // tenta de novo a cada minuto
    }
  );
