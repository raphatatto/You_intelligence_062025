'use client';

import { useMemo } from 'react';
import LeadsTable from '@/components/leads/LeadsTable';
import FiltroDistribuidora from '@/components/leads/FiltroDistribuidora';
import { leadsMock } from '@/app/data/leads';
import { useFilters } from '@/store/filters';
import { useSort } from '@/store/sort';
import FiltroSegmento from '@/components/leads/FiltroSegmento';


export default function LeadsPage() {
  const { estado, distribuidora, clearFilters, segmento, setEstado } = useFilters(); // ✅ pega os dois filtros
  const { order, setOrder } = useSort();

  const estados = useMemo<string[]>(
    () => Array.from(new Set(leadsMock.map((l) => l.estado))).sort(),
    []
  );

  const rows = useMemo(() => {
    let arr = [...leadsMock];

    // ✅ aplica filtro por estado, se houver
    if (estado) {
      arr = arr.filter((l) => l.estado === estado);
    }

    // ✅ aplica filtro por distribuidora, se houver
    if (distribuidora) {
      arr = arr.filter((l) => l.codigoDistribuidora === Number(distribuidora));
    }
    if (segmento) {
    arr = arr.filter((l) => l.CNAE === segmento);
}

    // ✅ aplica ordenação
    switch (order) {
      case 'dic-asc':
        arr.sort((a, b) => (a.dicMed ?? 0) - (b.dicMed ?? 0));
        break;
      case 'dic-desc':
        arr.sort((a, b) => (b.dicMed ?? 0) - (a.dicMed ?? 0));
        break;
      case 'fic-asc':
        arr.sort((a, b) => (a.ficMed ?? 0) - (b.ficMed ?? 0));
        break;
      case 'fic-desc':
        arr.sort((a, b) => (b.ficMed ?? 0) - (a.ficMed ?? 0));
        break;
      case 'none':
      default:
        break;
    }

    return arr;
  }, [estado, distribuidora, order]);

  return (
    <section className="space-y-6 p-6">
      <h1 className="text-2xl font-bold text-white">
        Leads ({rows.length})
      </h1>

      <div className="flex flex-wrap items-end gap-4 mb-6 bg-zinc-900 border border-zinc-700 rounded-xl px-6 py-4">
  {/* Estado + ordenação no mesmo bloco */}
  <div className="flex gap-4 items-center">
    <label className="text-sm text-white flex items-center gap-2">
      Estado:
      <select
        value={estado}
        onChange={(e) => setEstado(e.target.value)}
        className="bg-zinc-800 border border-zinc-600 rounded px-3 py-2 text-sm text-white"
      >
        <option value="">Todos</option>
        {estados.map((uf) => (
          <option key={uf} value={uf}>
            {uf}
          </option>
        ))}
      </select>
    </label>

    <label className="text-sm text-white flex items-center gap-2">
      Ordenar por:
      <select
        value={order}
        onChange={(e) => setOrder(e.target.value as any)}
        className="bg-zinc-800 border border-zinc-600 rounded px-3 py-2 text-sm text-white"
      >
        <option value="none">–</option>
        <option value="dic-asc">DIC Crescente</option>
        <option value="dic-desc">DIC Decrescente</option>
        <option value="fic-asc">FIC Crescente</option>
        <option value="fic-desc">FIC Decrescente</option>
      </select>
    </label>
  </div>
  <FiltroDistribuidora />
  <FiltroSegmento />
  <button
    onClick={clearFilters}
    className="text-sm bg-zinc-800 border border-zinc-600 text-white rounded px-4 py-2 hover:bg-zinc-700 transition">
    Limpar filtros
  </button>
  </div>
      <LeadsTable rows={rows} />
    </section>
  );
}
