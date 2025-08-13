'use client'

import { useMemo, useState, ChangeEvent } from 'react'
import LeadsTable from '@/components/leads/LeadsTable'
import FiltroDistribuidora from '@/components/leads/FiltroDistribuidora'
import FiltroSegmento from '@/components/leads/FiltroSegmento'
import { useFilters } from '@/store/filters'
import { useSort } from '@/store/sort'
import { useLeads } from '@/services/leads'
import { CNAE_SEGMENTOS } from '@/utils/cnae'
import { DISTRIBUIDORAS_MAP } from '@/utils/distribuidoras'
import { stripDiacritics } from '@/utils/stripDiacritics'
import { FileDown, Download, ChevronLeft, ChevronRight, Filter, Search, X } from 'lucide-react'
import * as XLSX from 'xlsx'
import type { Lead } from '@/app/types/lead'

const ITEMS_POR_PAGINA = 10

function exportarParaExcel(leadsParaExportar: Lead[], nomeArquivo = 'leads.xlsx') {
  const worksheet = XLSX.utils.json_to_sheet(leadsParaExportar)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Leads')
  XLSX.writeFile(workbook, nomeArquivo)
}

export default function LeadsPage() {
  const [pagina, setPagina] = useState(1)
  const [buscaInput, setBuscaInput] = useState('')
  const { estado, distribuidora, segmento, tipo, clearFilters, setEstado, setBusca, busca, setTipo } = useFilters()
  const { order, setOrder } = useSort()
  const { leads, isLoading, error } = useLeads()

  const estados = useMemo(() => {
  const values = leads
    .map(l => l.estado)
    .filter((uf): uf is string => typeof uf === 'string' && uf.length > 0)

  return Array.from(new Set(values)).sort()
}, [leads])

  const leadsFiltrados = useMemo<Lead[]>(() => {
    let arr = [...leads]

    const filtroEstado = estado.trim().toLowerCase()
    const filtroDistribuidora = distribuidora.trim()
    const filtroSegmento = segmento.trim()
    const filtroTipo = tipo.trim()

    if (filtroEstado)
      arr = arr.filter((l) => l.estado?.toLowerCase() === filtroEstado)

    if (filtroDistribuidora)
      arr = arr.filter((l) => l.distribuidora === filtroDistribuidora)

    if (filtroSegmento)
      arr = arr.filter((l) => l.cnae === filtroSegmento)

    if (filtroTipo)
      arr = arr.filter((l) => l.classe === filtroTipo)

    if (busca) {
      const term = stripDiacritics(busca.toLowerCase())

      arr = arr.filter((l) => {
        const estado = stripDiacritics(l.estado?.toLowerCase() ?? '')
        const cnae = stripDiacritics(l.cnae?.toLowerCase() ?? '')
        const distribuidora = stripDiacritics(l.distribuidora?.toLowerCase() ?? '')
        const segmentoNome = stripDiacritics(l.cnae?.toLowerCase() ?? '')
        const segmentoLead = stripDiacritics(l.segmento?.toLowerCase() ?? '')

        return (
          estado.includes(term) ||
          cnae.includes(term) ||
          distribuidora.includes(term) ||
          segmentoNome.includes(term) ||
          segmentoLead.includes(term)
        )
      })
    }

    switch (order) {
      case 'dic-asc': arr.sort((a, b) => (a.dicMed ?? 0) - (b.dicMed ?? 0)); break
      case 'dic-desc': arr.sort((a, b) => (b.dicMed ?? 0) - (a.dicMed ?? 0)); break
      case 'fic-asc': arr.sort((a, b) => (a.ficMed ?? 0) - (b.ficMed ?? 0)); break
      case 'fic-desc': arr.sort((a, b) => (b.ficMed ?? 0) - (a.ficMed ?? 0)); break
    }

    return arr
  }, [leads, estado, distribuidora, segmento, order, busca, tipo])

  const totalPaginas = Math.ceil(leadsFiltrados.length / ITEMS_POR_PAGINA)
  const inicio = (pagina - 1) * ITEMS_POR_PAGINA
  const fim = inicio + ITEMS_POR_PAGINA
  const leadsPagina = leadsFiltrados.slice(inicio, fim)

  const irParaPagina = (p: number) => {
    if (p >= 1 && p <= totalPaginas) setPagina(p)
  }

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  )

  if (error) return (
    <div className="bg-red-900/20 border border-red-700 rounded-xl p-6 text-center">
      <p className="text-red-400">Erro ao carregar leads: {error.message}</p>
    </div>
  )

  return (
    <section className="space-y-6 p-4 md:p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Leads</h1>
          <p className="text-sm text-zinc-400">
            {leadsFiltrados.length} {leadsFiltrados.length === 1 ? 'lead encontrado' : 'leads encontrados'}
          </p>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => exportarParaExcel(leadsPagina, 'leads-filtrados.xlsx')}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-3 py-2 rounded-md text-sm transition-colors"
          >
            <FileDown size={16} /> Exportar Página
          </button>
          <button
            onClick={() => exportarParaExcel(leadsFiltrados, 'leads-filtrados-completos.xlsx')}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-500 text-white px-3 py-2 rounded-md text-sm transition-colors"
          >
            <Download size={16} /> Exportar Todos
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-zinc-900/80 border border-zinc-700 rounded-xl p-4 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-zinc-300">
            <Filter size={16} />
            <span>Filtros</span>
          </div>
          <button
            onClick={() => {
              clearFilters()
              setBuscaInput('')
              setPagina(1)
            }}
            className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300"
          >
            <X size={14} /> Limpar filtros
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="space-y-1">
            <label className="text-xs text-zinc-400">Estado</label>
            <select
              value={estado}
              onChange={(e) => setEstado(e.target.value)}
              className="w-full bg-zinc-800 text-sm text-white border border-zinc-700 px-3 py-2 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos os estados</option>
              {estados.map((uf) => (
                <option key={uf} value={uf}>{uf.toUpperCase()}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-xs text-zinc-400">Tipo</label>
            <select
              value={tipo}
              onChange={(e) => setTipo(e.target.value)}
              className="w-full bg-zinc-800 text-sm text-white border border-zinc-700 px-3 py-2 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos os tipos</option>
              <option value="ucmt">UCMT</option>
              <option value="ucbt">UCBT</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-xs text-zinc-400">Ordenar por</label>
            <select
              value={order}
              onChange={(e) => setOrder(e.target.value as any)}
              className="w-full bg-zinc-800 text-sm text-white border border-zinc-700 px-3 py-2 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="none">Padrão</option>
              <option value="dic-asc">DIC (menor primeiro)</option>
              <option value="dic-desc">DIC (maior primeiro)</option>
              <option value="fic-asc">FIC (menor primeiro)</option>
              <option value="fic-desc">FIC (maior primeiro)</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-xs text-zinc-400">Buscar</label>
            <div className="relative">
              <input
                type="text"
                placeholder="Digite para buscar..."
                value={buscaInput}
                onChange={(e) => setBuscaInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && setBusca(buscaInput)}
                className="w-full bg-zinc-800 text-sm text-white border border-zinc-700 px-3 py-2 pl-9 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-500" />
              {buscaInput && (
                <button
                  onClick={() => {
                    setBuscaInput('')
                    setBusca('')
                  }}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
                >
                  <X size={16} />
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FiltroDistribuidora />
          <FiltroSegmento />
        </div>
      </div>

      {/* Tabela */}
      <LeadsTable rows={leadsPagina} />

      {/* Paginação */}
      {totalPaginas > 1 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-6">
          <div className="text-sm text-zinc-400">
            Mostrando {inicio + 1}-{Math.min(fim, leadsFiltrados.length)} de {leadsFiltrados.length} leads
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => irParaPagina(pagina - 1)}
              disabled={pagina === 1}
              className="flex items-center gap-1 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={16} /> Anterior
            </button>

            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, totalPaginas) }, (_, i) => {
                let pageNum
                if (totalPaginas <= 5) {
                  pageNum = i + 1
                } else if (pagina <= 3) {
                  pageNum = i + 1
                } else if (pagina >= totalPaginas - 2) {
                  pageNum = totalPaginas - 4 + i
                } else {
                  pageNum = pagina - 2 + i
                }

                return (
                  <button
                    key={pageNum}
                    onClick={() => irParaPagina(pageNum)}
                    className={`w-8 h-8 rounded-md flex items-center justify-center text-sm ${
                      pagina === pageNum
                        ? 'bg-blue-600 text-white'
                        : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300'
                    }`}
                  >
                    {pageNum}
                  </button>
                )
              })}
            </div>

            <button
              onClick={() => irParaPagina(pagina + 1)}
              disabled={pagina === totalPaginas}
              className="flex items-center gap-1 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Próxima <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </section>
  )
}