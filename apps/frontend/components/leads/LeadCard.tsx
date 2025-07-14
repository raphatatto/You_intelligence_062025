// components/leads/LeadCard.tsx
import { Lead } from '@/app/types/lead'

export function LeadCard({ lead }: { lead: Lead }) {
  return (
    <div className="rounded-xl bg-white shadow p-4 border border-gray-100 hover:shadow-lg transition">
      <h3 className="font-semibold text-lg">{lead.segmento_desc || 'Segmento desconhecido'}</h3>
      <p className="text-sm text-gray-500">{lead.municipio_nome}, {lead.municipio_uf}</p>

      <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
        <div>
          <span className="text-gray-400">Classe:</span>
          <span className="block font-medium">{lead.classe_desc}</span>
        </div>
        <div>
          <span className="text-gray-400">Origem:</span>
          <span className="block font-medium">{lead.origem}</span>
        </div>
        <div>
          <span className="text-gray-400">DIC Médio:</span>
          <span className="block font-medium">{lead.media_dic ?? '—'}</span>
        </div>
        <div>
          <span className="text-gray-400">FIC Médio:</span>
          <span className="block font-medium">{lead.media_fic ?? '—'}</span>
        </div>
      </div>
    </div>
  )
}
