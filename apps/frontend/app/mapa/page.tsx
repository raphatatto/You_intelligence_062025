'use client'

import MapView from '@/components/mapa/MapView'
import { useLeads } from '@/services/leads'
import { useSearchParams } from 'next/navigation'
import { useFilters } from '@/store/filters'
import { useSort } from '@/store/sort'
import { DISTRIBUIDORAS_MAP } from '@/utils/distribuidoras'
import FiltroSegmento from '@/components/leads/FiltroSegmento'
import { Filter, X } from 'lucide-react'

export default function MapaPage() {
  const {
    estado,
    setEstado,
    distribuidora,
    setDistribuidora,
    segmento,
    clearFilters,
  } = useFilters()

  const { order } = useSort()
  const { leads = [] } = useLeads()

  const params = useSearchParams()
  const selectedId = params?.get('id') ?? null

  const rows = (() => {
    let arr = leads

    if (estado) {
      arr = arr.filter((l) => l.estado === estado)
    }

    if (distribuidora) {
      arr = arr.filter((l) => String(l.codigoDistribuidora) === distribuidora)
    }

    if (segmento)
      arr = arr.filter((l) => l.cnae === segmento)

    switch (order) {
      case 'dic-asc':
        arr.sort((a, b) => (a.dicMed ?? 0) - (b.dicMed ?? 0))
        break
      case 'dic-desc':
        arr.sort((a, b) => (b.dicMed ?? 0) - (a.dicMed ?? 0))
        break
      case 'fic-asc':
        arr.sort((a, b) => (a.ficMed ?? 0) - (b.ficMed ?? 0))
        break
      case 'fic-desc':
        arr.sort((a, b) => (b.ficMed ?? 0) - (a.ficMed ?? 0))
        break
    }

    return arr
  })()

  const estadosUnicos = [...new Set(leads.map((l) => l.estado).filter(Boolean))].sort()
  const distribuidorasUnicas = [...new Set(leads.map((l) => l.codigoDistribuidora).filter((cod) => cod in DISTRIBUIDORAS_MAP))]

  return (
    <div className="flex flex-col h-screen bg-zinc-950">
      {/* Filtros */}
      <div className="px-6 py-4 bg-zinc-900/80 border-b border-zinc-700 backdrop-blur-sm">
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-zinc-300">
              <Filter size={18} className="text-blue-400" />
              <span>Filtros do Mapa</span>
            </div>
            <button
              onClick={clearFilters}
              className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300 transition-colors"
            >
              <X size={16} /> Limpar tudo
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Estado */}
            <div className="space-y-1">
              <label className="text-xs text-zinc-400">Estado</label>
              <select
                value={estado}
                onChange={(e) => setEstado(e.target.value)}
                className="w-full bg-zinc-800 text-sm text-white border border-zinc-700 px-3 py-2 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todos os estados</option>
                {estadosUnicos.map((uf) => (
                  <option key={uf} value={uf}>
                    {uf.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            {/* Distribuidora */}
            <div className="space-y-1">
              <label className="text-xs text-zinc-400">Distribuidora</label>
              <select
                value={distribuidora}
                onChange={(e) => setDistribuidora(e.target.value)}
                className="w-full bg-zinc-800 text-sm text-white border border-zinc-700 px-3 py-2 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todas as distribuidoras</option>
                {distribuidorasUnicas.map((cod) => (
                  <option key={cod} value={cod}>
                    {DISTRIBUIDORAS_MAP[cod]}
                  </option>
                ))}
              </select>
            </div>

            {/* Segmento CNAE */}
            <FiltroSegmento />

            {/* Contador */}
            <div className="flex items-end">
              <div className="w-full bg-zinc-800/50 border border-zinc-700 rounded-md px-3 py-2">
                <p className="text-xs text-zinc-400">Leads encontrados</p>
                <p className="text-white font-medium">{rows.length}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mapa */}
      <div className="flex-1 relative">
        <MapView leads={rows} selectedId={selectedId} />
      </div>
    </div>
  )
}