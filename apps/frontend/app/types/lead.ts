// … (seu código existente exportando `Lead`)

export type Lead = {
  id: string
  nome: string | null
  cnpj: string | null
  classe: string
  subgrupo: string | null
  modalidade: string
  estado: string | null
  municipio: string | null
  distribuidora: string
  potencia: number
  latitude: number | null
  longitude: number | null
  segmento: string
  status: string
  cnae: string
  dicMed: number | null
  ficMed: number | null
  dicMes: number | null
  ficMes: number | null
  // … quaisquer outros campos que você já tenha
}

// **Adicione este tipo para tipar o envelope da API**
export type LeadList = {
  total: number
  items: Lead[]
}
