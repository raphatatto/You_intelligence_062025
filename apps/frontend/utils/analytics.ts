// utils/analytics.ts
import { Lead } from '@/app/types/lead';

export function countByEstado(leads: Lead[]) {
  const counts: Record<string, number> = {};
  for (const l of leads) {
    counts[l.estado] = (counts[l.estado] || 0) + 1;
  }
  return Object.entries(counts).map(([estado, total]) => ({ estado, total }));
}

export function calcularEnergiaMapeada(leads: Lead[]) {
  return leads.reduce((total, l) => total + (l.dicMed ?? 0), 0);
}