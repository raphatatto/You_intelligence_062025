// lib/market.ts
export const REVALIDATE_SECONDS = 60 * 60 * 6; // 6h

// URL base da sua FastAPI (defina em .env/.env.local)
const NEXT_PUBLIC_API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

type AnyRec = Record<string, any>;

function stripAccents(s: string) {
  return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}
function keyMun(s: string) {
  return stripAccents(s).toLowerCase().trim();
}
function getMunicipioName(row: AnyRec): string | null {
  const keys = ['municipio', 'MUNICIPIO', 'mun', 'MUN', 'Municipio', 'city', 'cidade'];
  for (const k of keys) if (row[k]) return String(row[k]);
  return null;
}

function buildMetrics(rows: AnyRec[]) {
  const total = rows.length;

  const first = rows[0] ?? {};
  const fonteKey = ['TIP_SIST', 'fonte', 'FONTE', 'tipo_sistema', 'tipo']
    .find(k => first?.[k] != null);

  const fontesCount: Record<string, number> = {};
  if (fonteKey) {
    for (const r of rows) {
      const f = String(r[fonteKey] ?? 'Não informado');
      fontesCount[f] = (fontesCount[f] ?? 0) + 1;
    }
  }
  const fontesGeracao = Object.entries(fontesCount)
    .map(([name, value]) => ({ name, value }));

  const mesKey = ['MES', 'mes', 'MONTH', 'month'].find(k => first?.[k] != null);
  let consumoMensal: { mes: string; consumo: number }[] | null = null;
  if (mesKey) {
    const counter: Record<string, number> = {};
    for (const r of rows) {
      const m = String(r[mesKey]);
      counter[m] = (counter[m] ?? 0) + 1;
    }
    consumoMensal = Object.entries(counter)
      .map(([mes, consumo]) => ({ mes, consumo }))
      .sort((a, b) => a.mes.localeCompare(b.mes, undefined, { numeric: true }));
  }

  const tarifaKey = ['tarifa', 'TARIFA', 'valor_kwh', 'VALOR_KWH']
    .find(k => rows.some(r => r[k] != null));
  let tarifa: number | null = null;
  if (tarifaKey) {
    const vals = rows.map(r => Number(r[tarifaKey])).filter(v => Number.isFinite(v));
    if (vals.length) tarifa = vals.reduce((a, b) => a + b, 0) / vals.length;
  }

  const renovaveisSet = new Set(['SOLAR', 'FOTOVOLTAI', 'EOLICA', 'HIDR']);
  let renovaveis: number | null = null;
  if (fonteKey) {
    let ok = 0;
    for (const r of rows) {
      const f = String(r[fonteKey] ?? '').toUpperCase();
      if ([...renovaveisSet].some(tag => f.includes(tag))) ok++;
    }
    renovaveis = rows.length ? (ok / rows.length) * 100 : null;
  }

  const distKey = ['distribuidora', 'DISTRIBUIDORA', 'DIST', 'DIST_NOME', 'CONCESSIONARIA']
    .find(k => first?.[k] != null);
  const distribuidoras = distKey
    ? Array.from(new Set(rows.map(r => r[distKey]).filter(Boolean))).map(String)
    : [];

  return { total, tarifa, renovaveis, consumoMensal, fontesGeracao, distribuidoras };
}

export type MarketIndex = {
  index: Record<string, { rows: AnyRec[]; metrics: ReturnType<typeof buildMetrics> }>;
  nomes: Record<string, string>;
};

async function getJSON(path: string, revalidate = REVALIDATE_SECONDS) {
  const res = await fetch(`${NEXT_PUBLIC_API_BASE}${path}`, { next: { revalidate } });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`Falha ao buscar ${path}: ${res.status} ${res.statusText}${body ? ` — ${body}` : ''}`);
  }
  return res.json();
}

export async function getMarketIndexData(): Promise<MarketIndex> {
  // Busca as 4 fontes em paralelo
  const [ucmtSP, ucbtSP, ucbtRJ, ucmtRJ] = await Promise.all([
    getJSON('/ucmt-sp'),
    getJSON('/ucbt-sp'),
    getJSON('/ucbt-rj'),
    getJSON('/ucmt-rj'),
  ]) as [AnyRec[], AnyRec[], AnyRec[], AnyRec[]];

  const all = [...ucmtSP, ...ucbtSP, ...ucbtRJ, ...ucmtRJ];

  // Indexa por município
  const index: Record<string, { rows: AnyRec[]; metrics: ReturnType<typeof buildMetrics> }> = {};
  for (const row of all) {
    const m = getMunicipioName(row);
    if (!m) continue;
    const k = keyMun(m);
    (index[k] ||= {
      rows: [],
      metrics: { total: 0, tarifa: null, renovaveis: null, consumoMensal: null, fontesGeracao: [], distribuidoras: [] }
    }).rows.push(row);
  }

  // Pré-calcula métricas
  for (const k of Object.keys(index)) {
    index[k].metrics = buildMetrics(index[k].rows);
  }

  // Mapa de nomes bonitos
  const nomes: Record<string, string> = {};
  for (const row of all) {
    const m = getMunicipioName(row);
    if (m) nomes[keyMun(m)] = m;
  }

  return { index, nomes };
}
