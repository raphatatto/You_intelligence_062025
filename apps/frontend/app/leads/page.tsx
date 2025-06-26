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
import { Download, FileDown } from 'lucide-react'
import * as XLSX from 'xlsx'
import type { Lead } from '@/app/types/lead'

function exportarParaExcel(leadsParaExportar: Lead[], nomeArquivo = 'leads.xlsx') {
  const worksheet = XLSX.utils.json_to_sheet(leadsParaExportar)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Leads')
  XLSX.writeFile(workbook, nomeArquivo)
}

export default function LeadsPage() {
  const [mostrarFiltros, setMostrarFiltros] = useState(false)
  const [buscaInput, setBuscaInput] = useState('')

  const { estado, distribuidora, segmento, clearFilters, setEstado, setBusca, busca } = useFilters()
  const { order, setOrder } = useSort()
  const { leads, total, isLoading, error } = useLeads()

  // ✅ Esses dois hooks devem vir antes de qualquer return condicional
  const estados = useMemo<string[]>(() => {
    return Array.from(
      new Set(
        leads
          .map((l) => l.estado)
          .filter((uf): uf is string => Boolean(uf))
      )
    ).sort()
  }, [leads])

  const rows = useMemo<Lead[]>(() => {
    let arr = [...leads]

    if (estado) arr = arr.filter((l) => l.estado === estado)
    if (distribuidora) arr = arr.filter((l) => Number(l.distribuidora) === Number(distribuidora))
    if (segmento) arr = arr.filter((l) => l.cnae === segmento)

    if (busca) {
      const term = stripDiacritics(busca.toLowerCase())
      arr = arr.filter((l) => {
        const nome = stripDiacritics(l.nome?.toLowerCase() ?? '')
        const uf = stripDiacritics(l.estado?.toLowerCase() ?? '')
        const cnae = stripDiacritics(l.cnae?.toLowerCase() ?? '')
        const distName = stripDiacritics((DISTRIBUIDORAS_MAP[l.distribuidora] ?? l.distribuidora).toString().toLowerCase())
        const segName = stripDiacritics((l.cnae && CNAE_SEGMENTOS[l.cnae]?.toLowerCase()) ?? '')

        return nome.includes(term) || uf.includes(term) || cnae.includes(term) || distName.includes(term) || segName.includes(term)
      })
    }

    switch (order) {
      case 'dic-asc':
        arr.sort((a, b) => (a.dicMed ?? 0) - (b.dicMed ?? 0)); break
      case 'dic-desc':
        arr.sort((a, b) => (b.dicMed ?? 0) - (a.dicMed ?? 0)); break
      case 'fic-asc':
        arr.sort((a, b) => (a.ficMed ?? 0) - (b.ficMed ?? 0)); break
      case 'fic-desc':
        arr.sort((a, b) => (b.ficMed ?? 0) - (a.ficMed ?? 0)); break
    }

    return arr
  }, [leads, estado, distribuidora, segmento, order, busca])

  // ✅ só aqui os returns condicionais
  if (isLoading) return <p className="p-6 text-white">Carregando…</p>
  if (error) return <p className="p-6 text-red-500">Erro ao carregar leads: {error.message}</p>

  return (
    <section className="space-y-6 p-6">
      <h1 className="text-2xl font-bold text-white">
        Leads ({rows.length} de {total})
      </h1>

      <button
        onClick={() => setMostrarFiltros((v) => !v)}
        className="flex items-center gap-2 bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded"
      >
        {mostrarFiltros ? 'Ocultar Filtros' : 'Mostrar Filtros'}
      </button>

      {mostrarFiltros && (
        <div className="flex flex-wrap items-end gap-4 p-4 bg-zinc-900 border border-zinc-700 rounded-xl">
          <label className="flex items-center gap-2 text-white text-sm">
            Estado:
            <select
              value={estado}
              onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                setEstado(e.target.value)
              }
              className="bg-zinc-800 text-xs text-white border border-zinc-600 px-2 py-1 rounded"
            >
              <option value="">Todos</option>
              {estados.map((uf) => (
                <option key={uf} value={uf}>
                  {uf}
                </option>
              ))}
            </select>
          </label>

          <label className="flex items-center gap-2 text-white text-sm">
            Ordenar por:
            <select
              value={order}
              onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                setOrder(e.target.value as any)
              }
              className="bg-zinc-800 text-xs text-white border border-zinc-600 px-2 py-1 rounded"
            >
              <option value="none">–</option>
              <option value="dic-asc">DIC ↑</option>
              <option value="dic-desc">DIC ↓</option>
              <option value="fic-asc">FIC ↑</option>
              <option value="fic-desc">FIC ↓</option>
            </select>
          </label>

          <input
            type="text"
            placeholder="Buscar..."
            value={buscaInput}
            onChange={(e) => setBuscaInput(e.target.value)}
            className="bg-zinc-800 text-xs text-white border border-zinc-600 px-2 py-1 rounded flex-1"
          />

          <button
            onClick={() => setBusca(buscaInput)}
            className="bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded text-xs"
          >
            Buscar
          </button>

          <FiltroDistribuidora />
          <FiltroSegmento />

          <button
            onClick={clearFilters}
            className="bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-xs"
          >
            Limpar filtros
          </button>
        </div>
      )}

      <div className="flex justify-end gap-2">
        <button
          onClick={() => exportarParaExcel(rows, 'leads-filtrados.xlsx')}
          className="flex items-center gap-1 bg-blue-500 hover:bg-blue-400 text-white px-3 py-1 rounded text-xs"
        >
          <FileDown size={14} /> Exportar Filtrados
        </button>
        <button
          onClick={() => exportarParaExcel(leads, 'leads-todos.xlsx')}
          className="flex items-center gap-1 bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded text-xs"
        >
          <Download size={14} /> Exportar Todos
        </button>
      </div>

      <LeadsTable rows={rows} />
    </section>
  )
}
