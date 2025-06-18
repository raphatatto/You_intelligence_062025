'use client';

import { useFilters } from '@/store/filters';
import { useLeads } from '@/services/leads';
import { DISTRIBUIDORAS_MAP } from '@/utils/distribuidoras';

export default function FiltroDistribuidora() {
  const { distribuidora, setDistribuidora } = useFilters();
  const { data: leads = [] } = useLeads();

  // Coleta os códigos únicos das distribuidoras nos dados
  const codigos = [...new Set(leads.map((l) => l.codigoDistribuidora))];

  return (
    <label className="text-sm text-white flex items-center gap-2">
      Distribuidora:
      <select
        value={distribuidora}
        onChange={(e) => setDistribuidora(e.target.value)}
        className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1 text-sm text-white"
      >
        <option value="">Todas</option>
        {codigos.map((cod) => (
          <option key={cod} value={cod}>
            {DISTRIBUIDORAS_MAP[cod] || `Distribuidora ${cod}`}
          </option>
        ))}
      </select>
    </label>
  );
}
