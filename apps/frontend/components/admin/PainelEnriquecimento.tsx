'use client'

import { useState } from 'react'
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function PainelEnriquecimento() {
  const { data, isLoading, error, mutate } = useSWR('/v1/admin/dashboard/resumo', fetcher)
  const [loading, setLoading] = useState(false)

  const handleEnriquecer = async () => {
    setLoading(true)
    try {
      const response = await fetch('/v1/admin/enrich/geo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lead_ids: [] }) // substitua por seleção real no futuro
      })

      if (!response.ok) throw new Error('Erro ao enriquecer via Google')

      await fetch('/v1/admin/enrich/cnpj', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lead_ids: [] })
      })

      await mutate()
    } catch (err) {
      console.error(err)
      alert('Erro ao iniciar enriquecimento.')
    } finally {
      setLoading(false)
    }
  }

  if (isLoading || !data) return <p>Carregando dados...</p>
  if (error) return <p>Erro ao carregar métricas.</p>

  const cards = [
    { label: 'Leads RAW', value: data.raw, color: 'bg-gray-200 text-gray-800' },
    { label: 'Parcialmente Enriquecidos', value: data.partially_enriched, color: 'bg-yellow-100 text-yellow-800' },
    { label: 'Enriquecidos', value: data.enriched, color: 'bg-green-100 text-green-800' },
    { label: 'Falhas', value: data.failed, color: 'bg-red-100 text-red-800' },
  ]

  return (
    <div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {cards.map((card) => (
          <div key={card.label} className={`rounded p-4 shadow text-center ${card.color}`}>
            <p className="text-sm font-medium">{card.label}</p>
            <p className="text-xl font-bold">{card.value}</p>
          </div>
        ))}
      </div>

      <button
        onClick={handleEnriquecer}
        disabled={loading}
        className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded"
      >
        {loading ? 'Processando...' : '⚙️ Iniciar Enriquecimento'}
      </button>
    </div>
  )
}
