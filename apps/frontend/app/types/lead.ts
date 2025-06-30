// Tipagem principal de um lead
export type Lead = {
  id: string // UUID vindo da API
  nome: string | null // pode ser nulo em alguns casos
  cnpj: string | null // opcional, dependendo do dado
  classe: string // ex: 'Comercial', 'Industrial', etc.
  subgrupo: string | null // ex: 'A4', 'B1', etc.
  modalidade: string // ex: 'Convencional', 'Horosazonal'
  estado: string | null // 'SP', 'RJ', etc.
  municipio: string | null // nome da cidade
  distribuidora: string // nome ou código da distribuidora
  potencia: number // em kW
  latitude: number | null // para exibir no mapa
  longitude: number | null
  segmento: string // ex: 'Alimentos', 'Educação', etc.
  status: string // ex: 'novo', 'em contato', etc.
  cnae: string // código CNAE
  dicMed: number | null // DIC médio
  ficMed: number | null // FIC médio
  dicMes: number | null // DIC no mês
  ficMes: number | null // FIC no mês

  // ⚠️ Dica: se tiver mais campos no futuro, use:
  // [key: string]: any
}

// Tipagem para o retorno paginado da API
export type LeadList = {
  total: number
  items: Lead[]
}