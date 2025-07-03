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
    <label className="text-sm text-white flex items-center gap-2">
      Distribuidora:
      <select
        value={distribuidora}
        onChange={(e) => setDistribuidora(e.target.value)}
        className="text-xs text-white bg-zinc-800 border border-zinc-600 px-3 py-1.5 rounded-md shadow-sm hover:border-zinc-500 focus:outline-none focus:ring-1 focus:ring-lime-500 transition"
      >
        <option value="">Todas</option>
        {codigosUsados.map((cod) => (
          <option key={cod} value={cod}>
            {DISTRIBUIDORAS_MAP[cod]}
          </option>
        ))}
      </select>
    </label>
  )
}
