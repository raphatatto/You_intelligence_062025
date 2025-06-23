// app/mapa/page.tsx
'use client';

import MapView from '@/components/mapa/MapView';
import { useLeads } from '@/services/leads';
import { useSearchParams } from 'next/navigation';
import { useFilters } from '@/store/filters';
import { useSort } from '@/store/sort';
import { DISTRIBUIDORAS_MAP } from '@/utils/distribuidoras';

export default function MapaPage() {
  
  const { estado, setEstado, setDistribuidora, distribuidora, clearFilters, segmento} = useFilters();  
  const { order  } = useSort();     

  const { data: leads = [], isLoading, error } = useLeads();
  const params      = useSearchParams();
  const idParam     = params?.get?.('id')?? null;
  const selectedId  = idParam ? Number(idParam) : null;

    const rows = (() => {
    let arr = leads;

    if (estado) {
      arr = arr.filter((l) => l.estado === estado);
    }

    if (distribuidora) {
      arr = arr.filter((l) => l.codigoDistribuidora === Number(distribuidora));
    }
    if (segmento) {
    arr = arr.filter((l) => l.CNAE === segmento);
    }

    switch (order) {
      case 'dic-asc':
        arr = [...arr].sort((a, b) => (a.dicMed ?? 0) - (b.dicMed ?? 0));
        break;
      case 'dic-desc':
        arr = [...arr].sort((a, b) => (b.dicMed ?? 0) - (a.dicMed ?? 0));
        break;
      case 'fic-asc':
        arr = [...arr].sort((a, b) => (a.ficMed ?? 0) - (b.ficMed ?? 0));
        break;
      case 'fic-desc':
        arr = [...arr].sort((a, b) => (b.ficMed ?? 0) - (a.ficMed ?? 0));
        break;
    }
    return arr;
  })();
    console.log({
    estadoSelecionado: estado,
    leadsAntes: leads.length,
    leadsDepois: rows.length,
    estados: [...new Set(leads.map((l) => l.estado))]
  });

return (
  <div className="flex flex-col h-screen">
    {/* Filtros */}
    <div className="px-6 py-4">
      <div className="flex flex-wrap items-center gap-4">
        <label className="text-sm text-white flex items-center gap-2">
          Estado:
          <select
            value={estado}
            onChange={(e) => setEstado(e.target.value)}
            className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1 text-sm text-white"
          >
            <option value="">Todos</option>
            {[...new Set(leads.map((l) => l.estado))].map((uf) => (
              <option key={uf} value={uf}>
                {uf}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-white flex items-center gap-2">
          Distribuidora:
          <select
            value={distribuidora}
            onChange={(e) => setDistribuidora(e.target.value)}
            className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1 text-sm text-white"
          >
            <option value="">Todas</option>
            {[...new Set(leads.map((l) => l.codigoDistribuidora))].map((cod) => (
              <option key={cod} value={cod}>
                {DISTRIBUIDORAS_MAP[cod] || `Distribuidora ${cod}`}
              </option>
            ))}
          </select>
        </label>

        <button
          onClick={clearFilters}
          className="text-sm bg-zinc-800 border border-zinc-600 text-white rounded px-3 py-1 hover:bg-zinc-700 transition"
        >
          Limpar filtros
        </button>
      </div>
    </div>

    {/* Mapa ocupa o restante da tela */}
    <div className="flex-1">
      <MapView leads={rows} selectedId={selectedId} />
    </div>
  </div>
);
}