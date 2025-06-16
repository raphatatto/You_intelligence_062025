export type Lead = {
  id: string;
  nome: string;
  lng: number;
  lat: number;
  status: 'novo' | 'qualificado' | 'contato';
  regiao: 'Norte' | 'Nordeste' | 'Centro-Oeste' | 'Sudeste' | 'Sul';
  estado: string;
  cidade: string;
  solucao: 'Solar' | 'Arbitragem' | 'Backup' | 'PeakShaving' | 'Outros';
};
