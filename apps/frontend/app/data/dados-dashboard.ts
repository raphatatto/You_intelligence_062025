// data/dados-dashboard.ts
import type { KpiDados, EnriqItem, QualityPoint, AlertItem } from '@/app/types/dados-dashboard';

export const kpis: KpiDados[] = [
  { label: 'Registros totais',        valor: '90 345 812' },
  { label: 'Última atualização',      valor: '2025-06-13 02:15' },
  { label: 'Novos no último batch',   valor: '214 006' },
];

export const gaugeQualidade = 82; 

export const enriquecimento: EnriqItem[] = [
  { atributo: 'Coordenadas', cobertura: 91 },
  { atributo: 'Classe consumo', cobertura: 78 },
  { atributo: 'CPF/CNPJ vinc.', cobertura: 66 },
];

export const serieQualidade: QualityPoint[] = [
  { mes: 'Jan', qualidade: 74 },
  { mes: 'Fev', qualidade: 77 },
  { mes: 'Mar', qualidade: 79 },
  { mes: 'Abr', qualidade: 81 },
  { mes: 'Mai', qualidade: 82 },
];

export const alerts: AlertItem[] = [
  { id: 'a1', mensagem: '5 % dos clientes da região Norte sem consumo 2024-Q4', severidade: 'warn' },
  { id: 'a2', mensagem: 'Novos códigos UC sem correspondência (2 134 registros)', severidade: 'crit' },
];
