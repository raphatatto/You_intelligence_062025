'use client'

import { useRouter } from 'next/navigation'
import type { Lead } from '@/app/types/lead'
import { useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { clsx } from 'clsx'
import { DISTRIBUIDORAS_MAP } from '@/utils/distribuidoras'
import { ArrowUpRight, ChevronRight } from 'lucide-react'

type Props = {
  rows: Lead[]
}

export default function LeadsTable({ rows }: Props) {
  const router = useRouter()
  const params = useSearchParams()
  const selectedId = params?.get('id') ?? null

  useEffect(() => {
    if (selectedId) {
      const el = document.getElementById(`lead-${selectedId}`)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
  }, [selectedId])

  if (!rows.length) {
    return (
      <div className="rounded-xl border border-zinc-700 bg-zinc-900 p-8 text-center">
        <p className="text-zinc-400">Nenhum lead encontrado</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-zinc-700 bg-zinc-900 shadow-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-zinc-800/80 backdrop-blur-sm">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider">ID</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider">DIC</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider">FIC</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider">CNAE</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider">Bairro</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider">Distribuidora</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider">Segmento</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-zinc-300 uppercase tracking-wider"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {rows.map((lead) => (
              <tr
                key={lead.id}
                id={`lead-${lead.id}`}
                onClick={() => router.push(`/mapa?id=${lead.id}`)}
                className={clsx(
                  "group cursor-pointer transition-colors",
                  lead.id === selectedId 
                    ? 'bg-lime-500/10 hover:bg-lime-500/15' 
                    : 'hover:bg-zinc-800/50'
                )}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className="font-mono text-xs bg-zinc-800/50 px-2 py-1 rounded">
                      {lead.id ? `${lead.id.slice(0, 8)}...` : '—'}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap">
                  <span className={clsx(
                    "px-2 py-1 rounded-full text-xs font-medium",
                    lead.dicMed ? (lead.dicMed > 3 ? 'bg-red-500/10 text-red-400' : 'bg-emerald-500/10 text-emerald-400') : 'bg-zinc-800/50 text-zinc-400'
                  )}>
                    {lead.dicMed?.toFixed(2) ?? '—'}
                  </span>
                </td>
                <td className="px-4 py-4 whitespace-nowrap">
                  <span className={clsx(
                    "px-2 py-1 rounded-full text-xs font-medium",
                    lead.ficMed ? (lead.ficMed > 10 ? 'bg-red-500/10 text-red-400' : 'bg-emerald-500/10 text-emerald-400') : 'bg-zinc-800/50 text-zinc-400'
                  )}>
                    {lead.ficMed?.toFixed(2) ?? '—'}
                  </span>
                </td>
                <td className="px-4 py-4 whitespace-nowrap max-w-[120px] truncate" title={lead.cnae}>
                  {lead.cnae ?? '—'}
                </td>
                <td className="px-4 py-4 whitespace-nowrap">
                  {lead.bairro ?? '—'}
                </td>
                <td className="px-4 py-4 whitespace-nowrap">
                  <span className="inline-flex items-center gap-1">
                    {DISTRIBUIDORAS_MAP[lead.distribuidora] ?? lead.distribuidora ?? '—'}
                  </span>
                </td>
                <td className="px-4 py-4 whitespace-nowrap max-w-[150px] truncate">
                  {lead.segmento ?? '—'}
                </td>
                <td className="px-4 py-4 text-right whitespace-nowrap">
                  <div className="flex justify-end">
                    <button className="opacity-0 group-hover:opacity-100 text-zinc-400 hover:text-white transition-opacity">
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Footer with pagination would go here */}
      <div className="bg-zinc-800/50 px-6 py-3 text-xs text-zinc-400 border-t border-zinc-800">
        Mostrando {rows.length} {rows.length === 1 ? 'lead' : 'leads'}
      </div>
    </div>
  )
}