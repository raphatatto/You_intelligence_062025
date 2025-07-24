'use client';

import { useFilters } from '@/store/filters';
import { useLeads } from '@/services/leads';
import { CNAE_SEGMENTOS } from '@/utils/cnae';

export default function FiltroSegmento() {
  const { segmento, setSegmento } = useFilters();
  const { leads = [] } = useLeads();

  const cnaesUnicos = [...new Set(leads.map((l) => l.cnae).filter(Boolean))];

  return (
    <div className="space-y-1 ">
      <label className="text-xs text-zinc-400">Segmento</label>
      <select 
        value={segmento}
        onChange={(e) => setSegmento(e.target.value)}
        className="w-full bg-zinc-800 text-sm text-white border border-zinc-700 px-3 py-2 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent "
      >
        <option value="">Todos os segmentos</option>
        {cnaesUnicos
          .filter((c): c is string => typeof c === 'string')
          .map((cnae) => (
            <option key={cnae} value={cnae} className=''>
              {CNAE_SEGMENTOS[cnae] || `CNAE ${cnae}`}
            </option>
          ))}
      </select>
    </div>
  );
}