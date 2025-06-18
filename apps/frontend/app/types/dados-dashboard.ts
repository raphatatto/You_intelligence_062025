export type KpiDados = { label: string; valor: number | string };
export type EnriqItem = { atributo: string; cobertura: number };   // %
export type QualityPoint = { mes: string; qualidade: number };     // %
export type AlertItem = { id: string; mensagem: string; severidade: 'info' | 'warn' | 'crit' };