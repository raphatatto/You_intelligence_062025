// types/lead.ts
export type Lead = {
  id: number;
  nome: string;
  lat: number;
  lng: number;
  estado: string;

  dicMes: number[];   // 12 itens
  ficMes: number[];   // 12 itens

  // calculados no front (ou já vindos do back):
  dicMed?: number;
  ficMed?: number;

  descricao: string;
  CNAE?: string;
};
