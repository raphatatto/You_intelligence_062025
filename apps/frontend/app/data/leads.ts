import type {SerieLeads} from '@/app/types/chart';
import type {Lead} from '@/app/types/lead'; 

export const mockLeads: SerieLeads[] = [
  {dia: '01', leads: 5},
  {dia: '02', leads: 8},
  {dia: '03', leads: 3},
  {dia: '04', leads: 9},
];

export const leads: Lead[] = [
  {id: '1', nome: 'Acme Ltda', lng: -23.724198, lat: -46.714637, status: 'qualificado'},
  {id: '2', nome: 'Beta S.A.', lng: -51.18, lat: -30.05, status: 'novo'},
];