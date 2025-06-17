// app/mapa/page.tsx
'use client';

import MapView from '@/components/mapa/MapView';
import { useLeads } from '@/services/leads';
import { useSearchParams } from 'next/navigation';
import { useFilters } from '@/store/filters';
import { useSort } from '@/store/sort';

export default function MapaPage() {

  const { estado } = useFilters();  
  const { order  } = useSort();     

  const { data: leads = [], isLoading, error } = useLeads();
  const params      = useSearchParams();
  const idParam     = params.get('id');
  const selectedId  = idParam ? Number(idParam) : null;

  const rows = (() => {
    let arr = !estado ? leads : leads.filter((l) => l.estado === estado);

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
  return (
    <div className="h-screen">
      <MapView leads={rows} selectedId={selectedId} />
    </div>
  );
}
