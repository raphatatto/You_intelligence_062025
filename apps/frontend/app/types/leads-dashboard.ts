export type KpiLead = { label: string; valor: number; meta?: number };
export type PorSolucao = { solucao: string; leads: number };
export type PorEstagio = { estagio: string; qtd: number };
export type SerieTemporal = { dia: string; leads: number };

export type LeadRow = {
  id: string;
  nome: string;
  solucao: string;
  estagio: string;
  potencial: number;
};
