export type Lead = {
  id: string
  dicMed: number
  ficMed: number
  cnae: string
  bairro: string
  cep: string
  estado: string
  distribuidora: string
  codigoDistribuidora: string 
  segmento: string
  descricao?: string
  potencia?: number; 
  lat: number
  lng: number
}
