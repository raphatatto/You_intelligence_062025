export type Lead = {
  id: string;
  nome: string;
  latitude: number;
  longitude: number;
  estado: string;

  dicMes: number[];
  ficMes: number[];
  dicMed?: number;
  ficMed?: number;

  descricao?: string;
  cnae?: string;
  distribuidora?: string;

  classe?: string;
  potencia?: number;
  segmento?: string;
  status?: string;
};
