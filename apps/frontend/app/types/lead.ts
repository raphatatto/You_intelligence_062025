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
  longitude: number
  latitude: number
  tipo: string
  segmento_desc:string
  municipio_nome:string
  municipio_uf:string
  classe_desc:string
  origem:string
  media_dic:number
  media_fic:number
}
