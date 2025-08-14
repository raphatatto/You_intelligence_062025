'use client'

import { useMemo } from 'react'
import { useFilters } from '@/store/filters'
import { useLeads } from '@/services/leads'
import { DISTRIBUIDORAS_MAP } from '@/utils/distribuidoras'

type LeadLike = { distribuidora?: string | null; codigoDistribuidora?: string | null }

const getDistCode = (l: LeadLike) =>
  (l.distribuidora ?? l.codigoDistribuidora ?? '').toString().trim()

const labelDist = (cod?: string | null) =>
  cod ? (DISTRIBUIDORAS_MAP as Record<string, string>)[cod] ?? cod : '—'

export default function FiltroDistribuidora() {
  const { distribuidora, setDistribuidora } = useFilters()
  const { leads } = useLeads()

  const opcoes = useMemo(() => {
    const usados = new Set<string>()
    for (const l of leads) {
      const cod = getDistCode(l)
      if (cod) usados.add(cod)
    }
    return Array.from(usados).sort((a, b) =>
      labelDist(a).localeCompare(labelDist(b), 'pt-BR')
    )
  }, [leads])

  return (
    <div className="space-y-1">
      <label className="text-xs text-zinc-400">Distribuidora</label>
      <select
        value={distribuidora}
        onChange={(e) => setDistribuidora(e.target.value)}
        className="w-full bg-zinc-800 text-sm text-white border border-zinc-700 px-3 py-2 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">Todas as distribuidoras</option>
        {opcoes.map((cod) => (
          <option key={cod} value={cod}>
            {labelDist(cod)}
          </option>
        ))}
      </select>
    </div>
  )
}
