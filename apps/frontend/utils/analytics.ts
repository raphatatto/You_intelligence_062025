// utils/analytics.ts
import { Lead } from '@/app/types/lead';
import { toNumberBR } from '@/utils/transformarDadosMensais'; 


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


export function calcularEnergiaMapeada(leads: Lead[]): number {
  let total = 0;

  leads.forEach((lead) => {
    for (let i = 1; i <= 12; i++) {
      const key = `ENE_${String(i).padStart(2, '0')}`;
      const valor = (lead as any)[key];
      total += toNumberBR(valor);
    }
  });

  return total;
}


export function filtrarLeadsComPotencial(leads: Lead[], potenciaMinima = 100): Lead[] {
  return leads.filter((l) => {
    // Potência: aceita `l.potencia` ou `PAC` vindo cru da API
    const pot = toNumberBR((l as any).potencia ?? (l as any).PAC);
    const hasPot = pot >= potenciaMinima;

    // CNAE presente e não vazio
    const hasCnae = !!l.cnae?.trim();

    // Coordenadas: usa os nomes do seu tipo (latitude/longitude)
    const lat = (l as any).latitude ?? (l as any).lat;
    const lng = (l as any).longitude ?? (l as any).lng;
    const hasCoords = lat != null && lng != null;

    return hasPot && hasCnae && hasCoords;
  });
}

