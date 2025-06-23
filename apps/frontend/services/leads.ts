import useSWR from 'swr';
import type { Lead } from '@/app/types/lead';
import { leadsMock } from '@/app/data/leads';

const base = process.env.NEXT_PUBLIC_API_BASE ?? ''; // "" enquanto não há back
const fetcher = (url: string) =>
  fetch(base + url).then(r => {
    if (!r.ok) throw new Error('api fail');
    return r.json();
  });

// export const useLeads = () =>
//   useSWR<Lead[]>(
//     base ? '/leads' : null,            // não faz fetch se base == ""
//     fetcher,
//     {
//       fallbackData: leadsMock,
//       revalidateOnFocus: false,
//       onErrorRetry: () => {},          // evita loop
//     }
//   );

  export async function getLeads(): Promise<Lead[]> {
  const res = await fetch('/mock/leads.json'); // depois trocamos essa URL
  if (!res.ok) throw new Error('Erro ao carregar leads');
  return res.json();
}

export function useLeads() {
  return useSWR('leads', getLeads); // chave "leads", usa a função acima
}
