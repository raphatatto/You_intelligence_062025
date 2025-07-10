// utils/analytics.ts
import { Lead } from '@/app/types/lead';

export function countByEstado(leads: Lead[]) {
  const counts: Record<string, number> = {};
  for (const l of leads) {
    counts[l.estado] = (counts[l.estado] || 0) + 1;
  }
  return Object.entries(counts).map(([estado, total]) => ({ estado, total }));
}

export function countByDistribuidora(leads: Lead[]) {
  const contagem: Record<string, number> = {};
  for (const lead of leads) {
    const dist = lead.distribuidora || 'Desconhecida';
    contagem[dist] = (contagem[dist] || 0) + 1;
  }
  return Object.entries(contagem).map(([nome, total]) => ({ nome, total }));
}

export function top10CNAE(leads: Lead[]) {
  const counts: Record<string, number> = {};

  for (const l of leads) {
    if (!l.cnae || l.cnae.trim() === '') continue; 
    const cnae = l.cnae;
    counts[cnae] = (counts[cnae] || 0) + 1;
  }

  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([nome, total]) => ({ nome, total }));
}

export function calcularEnergiaMapeada(leads: Lead[]) {
  const horasMes = 30 * 24; // 720h
  const totalKWh = leads.reduce((soma, l) => soma + ((l.potencia ?? 0) * horasMes), 0);
  const totalMWh = totalKWh / 1000;
  return totalMWh;
}


export function filtrarLeadsComPotencial(leads: Lead[], potenciaMinima = 100): Lead[] {
  return leads.filter(l =>
    l.potencia !== undefined &&
    l.potencia >= potenciaMinima &&
    l.cnae &&
    l.lat !== undefined &&
    l.lng !== undefined
  );
}