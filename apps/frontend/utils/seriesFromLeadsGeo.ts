// Agrega valores mensais varrendo as chaves do objeto (flexível a variações)
type AnyRec = Record<string, any>;

const MESES = Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, "0"));

function sumByRegex(items: AnyRec[], regexes: RegExp[]) {
  // retorna array [12] com soma por mês
  const acc = MESES.map(() => 0);
  for (const it of items || []) {
    const keys = Object.keys(it);
    for (const k of keys) {
      const m = regexes
        .map(rx => rx.exec(k))
        .find(Boolean);
      if (!m) continue;
      const mes = m[1]; // grupo da regex = "01"..."12"
      const idx = Number(mes) - 1;
      const raw = it[k];
      const val = typeof raw === "string" ? Number(raw.replace(",", ".")) : Number(raw);
      if (!Number.isFinite(val)) continue;
      acc[idx] += val;
    }
  }
  return acc;
}

export function buildSeriesFromLeads(leads: AnyRec[] | undefined) {
  // Energia kWh (aceita ENERGIA_01, KWH_01, ENERGIA01)
  const energiaSomas = sumByRegex(leads ?? [], [
    /^ENERGIA[_]?(\d{2})$/i,
    /^KWH[_]?(\d{2})$/i,
    /^ENERGIA_KWH[_]?(\d{2})$/i,
  ]);

  // Demanda kW (aceita DEMANDA_01, KW_01)
  const demandaSomas = sumByRegex(leads ?? [], [
    /^DEMANDA[_]?(\d{2})$/i,
    /^KW[_]?(\d{2})$/i,
  ]);

  // Indicadores (DIC em minutos, FIC em vezes)
  const dicSomas = sumByRegex(leads ?? [], [/^DIC[_]?(\d{2})$/i]);
  const ficSomas = sumByRegex(leads ?? [], [/^FIC[_]?(\d{2})$/i]);

  // Constrói nos formatos esperados pelos seus componentes
  const energiaMensal = MESES.map((m, i) => ({ mes: m, energia_kwh: Number(energiaSomas[i].toFixed(2)) }));
  const demandaMensal = MESES.map((m, i) => ({ mes: m, demanda_kw: Number(demandaSomas[i].toFixed(2)) }));
  const indicadoresMensais = MESES.map((m, i) => ({
    mes: m,
    dic_min: Number(dicSomas[i].toFixed(2)),
    fic_vezes: Number(ficSomas[i].toFixed(2)),
  }));

  return { energiaMensal, demandaMensal, indicadoresMensais };
}
