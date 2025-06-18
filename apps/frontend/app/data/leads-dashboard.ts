import type {
  KpiLead,
  PorSolucao,
  PorEstagio,
  SerieTemporal,
  LeadRow,
} from '@/app/types/leads-dashboard';

export const kpis: KpiLead[] = [
  { label: 'Leads gerados (mês)', valor: 428 },
  { label: 'Qualificados', valor: 179 },
  { label: 'Propostas enviadas', valor: 64 },
  { label: 'Taxa conversão', valor: 15 }, // %
];

export const porSolucao: PorSolucao[] = [
  { solucao: 'Solar Residencial', leads: 180 },
  { solucao: 'Solar Empresarial', leads: 120 },
  { solucao: 'Eficiência', leads: 60 },
  { solucao: 'Consultoria', leads: 68 },
];

export const porEstagio: PorEstagio[] = [
  { estagio: 'Novo', qtd: 220 },
  { estagio: 'Contato', qtd: 110 },
  { estagio: 'Proposta', qtd: 64 },
  { estagio: 'Fechado', qtd: 34 },
];

export const serieTempo: SerieTemporal[] = [
  { dia: '01', leads: 14 },
  { dia: '02', leads: 19 },
  { dia: '03', leads: 11 },
  { dia: '04', leads: 17 },
  { dia: '05', leads: 9 },
  { dia: '06', leads: 23 },
  { dia: '07', leads: 15 },
];

export const topLeads: LeadRow[] = [
  { id: '1', nome: 'ABC Metalúrgica', solucao: 'Solar Emp.', estagio: 'Proposta', potencial: 45000 },
  { id: '2', nome: 'Residencial Silva', solucao: 'Solar Res.', estagio: 'Contato',  potencial: 32000 },
  { id: '3', nome: 'Hotel do Vale',     solucao: 'Eficiência',estagio: 'Novo',      potencial: 28000 },
];
