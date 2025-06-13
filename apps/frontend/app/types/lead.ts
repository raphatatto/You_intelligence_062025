export type Lead = {
  id: string;
  nome: string;
  lng: number;
  lat: number;
  status: 'novo' | 'qualificado' | 'contato';
};
