import type {SerieLeads} from '@/app/types/chart';
import type {Lead} from '@/app/types/lead'; 
import { enrichLeads } from '@/utils/enrich';

export const mockLeads: SerieLeads[] = [
  {dia: '01', leads: 5},
  {dia: '02', leads: 8},
  {dia: '03', leads: 3},
  {dia: '04', leads: 9},
];

const raw: Lead[] = [
  {
    id: 1,
    nome: 'Beta (SP)',
    lat: -23.724966992368397,
    lng: -46.71432532196724,
    estado: 'SP',
    dicMes: [1.3, 1.1, 1.4, 1.2, 1.3, 1.2, 1.5, 1.6, 1.4, 1.3, 1.2, 1.1],
    ficMes: [4, 2, 3, 2, 2, 2, 3, 4, 3, 3, 2, 2],
    descricao: 'Empresa Beta localizada em São Paulo, especializada em soluções de energia solar.',
    CNAE: '3511-3/01',
  },
  {
    id: 2,
    nome: 'Beta (RS)',
    lat: -30.05,
    lng: -51.18,
    estado: 'RS',
    dicMes: [2.0, 1.1, 1.4, 1.2, 1.3, 1.2, 1.5, 1.6, 1.4, 1.3, 1.2, 1.1],
    ficMes: [2, 2, 3, 2, 2, 2, 3, 4, 3, 3, 2, 2],
    descricao: 'Empresa Beta localizada no Rio Grande do Sul, especializada em soluções de energia solar.',
    CNAE: '3511-3/01',
  },
];
export const leadsMock = enrichLeads(raw);


