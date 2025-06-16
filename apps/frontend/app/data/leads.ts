import type {SerieLeads} from '@/app/types/chart';
import type {Lead} from '@/app/types/lead'; 

export const mockLeads: SerieLeads[] = [
  {dia: '01', leads: 5},
  {dia: '02', leads: 8},
  {dia: '03', leads: 3},
  {dia: '04', leads: 9},
];

export const leadsMock: Lead[] = [
  { id: "1", nome: 'ABC', lat: -23.54, lng: -46.63, dic: "2", fic: "1"},
  { id: "2", nome: 'Beta', lat: -30.05, lng: -51.18,  dic: "1", fic: "2"},
];