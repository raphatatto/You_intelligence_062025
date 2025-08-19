import type { Lead } from '@/app/types/lead'
function toNumberBR(v: any): number {
  if (v == null) return 0;
  if (typeof v === 'number') return isFinite(v) ? v : 0;
  if (typeof v === 'string') {
    const s = v.replace(/\./g, '').replace(',', '.').trim(); // "1.234,5" -> "1234.5"
    const n = Number(s);
    return isFinite(n) ? n : 0;
  }
  return 0;
}
export function gerarDadosMensais(leads: Lead[]) {
  const energia = Array(12).fill(0);
  const demanda = Array(12).fill(0);
  const dic = Array(12).fill(0);
  const fic = Array(12).fill(0);

  const totalLeads = leads.length || 1;

  leads.forEach(lead => {
    for (let i = 1; i <= 12; i++) {
      energia[i-1] += toNumberBR((lead as any)[`ENE_${String(i).padStart(2,"0")}`]);
      demanda[i-1] += toNumberBR((lead as any)[`DEM_${String(i).padStart(2,"0")}`]);
      dic[i-1]     += toNumberBR((lead as any)[`DIC_${String(i).padStart(2,"0")}`]);
      fic[i-1]     += toNumberBR((lead as any)[`FIC_${String(i).padStart(2,"0")}`]);

    }
  });

  const energia_mensal = energia.map((valor, i) => ({
    mes: String(i + 1).padStart(2, "0"),
    energia_kwh: +(valor / totalLeads).toFixed(2)  
  }));

  const demanda_mensal = demanda.map((valor, i) => ({
    mes: String(i + 1).padStart(2, "0"),
    demanda_kw: +(valor / totalLeads).toFixed(2)
  }));

  const dic_fic_mensal = dic.map((valor, i) => ({
    mes: String(i + 1).padStart(2, "0"),
    dic: +(dic[i] / totalLeads).toFixed(2),
    fic: +(fic[i] / totalLeads).toFixed(2),
  }));

  return { energia_mensal, demanda_mensal, dic_fic_mensal };
}
