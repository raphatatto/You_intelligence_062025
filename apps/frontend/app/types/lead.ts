export type Lead = {
  id: string
  ucId: string
  descricao?: string | null
  cnae?: string | null
  cnaeDescricao?: string | null
  segmento?: string | null
  tipo?: string | null
  bairro?: string | null
  cep?: string | null
  distribuidora?: string | null
  municipio?: string | null
  estado?: string | null
  latitude?: number | null
  longitude?: number | null
  potencia?: number | null
  dicMed?: number | null
  ficMed?: number | null
  energiaMediaTotal?: number | null
  demandaMediaContratada?: number | null
  nomeFantasia?: string | null
  razaoSocial?: string | null
  cnpj?: string | null
  telefone?: string | null
  email?: string | null
  site?: string | null
  receitaSituacao?: string | null
  receitaAbertura?: string | null
  receitaNatureza?: string | null
  receitaPorte?: string | null
  receitaCapitalSocial?: string | null
  receitaAtividadePrincipal?: string | null
  receitaMunicipio?: string | null
  receitaUf?: string | null
  enrichedAt?: string | null
}
