// components/leads/FiltroSegmento.tsx
'use client';

import { useFilters } from '@/store/filters';
import { useLeads } from '@/services/leads';
import { CNAE_SEGMENTOS } from '@/utils/cnae';

export default function FiltroSegmento() {
  const { segmento, setSegmento } = useFilters();
  const { data: leads = [] } = useLeads();

  const cnaesUnicos = [...new Set(leads.map((l) => l.CNAE).filter(Boolean))];

  return (
    <label className="text-sm text-white flex items-center gap-2">
      Segmento:
      <select
        value={segmento}
        onChange={(e) => setSegmento(e.target.value)}
        className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1 text-sm text-white"
      >
        <option value="">Todos</option>
      {cnaesUnicos
        .filter((c): c is string => typeof c === 'string') 
        .map((cnae) => (
        <option key={cnae} value={cnae}>
        {CNAE_SEGMENTOS[cnae] || `CNAE ${cnae}`}
        </option>
        ))}
      </select>
    </label>
  );
}
