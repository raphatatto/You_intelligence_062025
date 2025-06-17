// app/leads/page.tsx
'use client';

import { useMemo } from 'react';
import LeadsTable   from '@/components/leads/LeadsTable';
import FiltersBar   from '@/components/leads/FiltersBar';
import { leadsMock } from '@/app/data/leads';         
import { useFilters } from '@/store/filters';
import { useSort }    from '@/store/sort';

export default function LeadsPage() {
  const { estado } = useFilters();   
  const { order  } = useSort();      


  const estados = useMemo<string[]>(
    () => Array.from(new Set(leadsMock.map(l => l.estado))).sort(),
    []
  );

  const rows = useMemo(() => {
    let arr = estado ? leadsMock.filter(l => l.estado === estado) : leadsMock;
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
      case 'none':
      default:
        break; 
    }
    return arr;
  }, [estado, order]);

  return (
    <section className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">
        Leads ({rows.length})
      </h1>
      <FiltersBar estados={estados} />
      <LeadsTable rows={rows} />
    </section>
  );
}
