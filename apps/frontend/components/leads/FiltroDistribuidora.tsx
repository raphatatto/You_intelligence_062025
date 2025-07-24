'use client'

import { useFilters } from '@/store/filters'
import { useLeads } from '@/services/leads'
import { DISTRIBUIDORAS_MAP } from '@/utils/distribuidoras'

export default function FiltroDistribuidora() {
  const { distribuidora, setDistribuidora } = useFilters()
  const { leads } = useLeads()

  // Coleta apenas códigos presentes no dicionário
  const codigosValidos = Object.keys(DISTRIBUIDORAS_MAP)

  // Pega os códigos únicos encontrados nos leads (e que estão no mapa)
  const codigosUsados = [...new Set(
    leads.map((l) => l.codigoDistribuidora).filter((cod) => codigosValidos.includes(cod))
  )]

  return (
    <div className="space-y-1">
      <label className="text-xs text-zinc-400">Distribuidora</label>
      <select
        value={distribuidora}
        onChange={(e) => setDistribuidora(e.target.value)}
        className="w-full bg-zinc-800 text-sm text-white border border-zinc-700 px-3 py-2 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">Todas as distribuidoras</option>
        {codigosUsados.map((cod) => (
          <option key={cod} value={cod}>
            {DISTRIBUIDORAS_MAP[cod]}
          </option>
        ))}
      </select>
    </div>
  )
}