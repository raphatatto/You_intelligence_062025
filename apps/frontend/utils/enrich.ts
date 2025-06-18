import type { Lead } from '@/app/types/lead';

export function enrichLeads(raw: Lead[]): Lead[] {
  return raw.map((l) => ({
    ...l,
    dicMed: +(l.dicMes.reduce((s, v) => s + v, 0) / l.dicMes.length).toFixed(2),
    ficMed: +(l.ficMes.reduce((s, v) => s + v, 0) / l.ficMes.length).toFixed(2),
  }));
}
