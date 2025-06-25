'use client';

import { useFilters } from '@/store/filters';
import { useSort, SortKey } from '@/store/sort';

export default function FiltersBar({ estados }: { estados: string[] }) {
  const { estado, setEstado } = useFilters();
  const { order, setOrder } = useSort();

  return (
    <div className="flex flex-wrap items-center gap-6 rounded-xl border border-zinc-700 bg-zinc-900 p-4 shadow-md">
      {/* ────────────── seletor de UF ────────────── */}
      <label className="text-sm flex items-center gap-2 text-zinc-300">
        <span>Estado:</span>
        <select
          value={estado}
          onChange={(e) => setEstado(e.target.value)}
          className="rounded border border-zinc-600 bg-zinc-800 px-2 py-1 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-lime-500"
        >
          <option value="">Todos</option>
          {estados.map((uf) => (
            <option key={uf} value={uf}>
              {uf}
            </option>
          ))}
        </select>
      </label>

      {/* ────────────── seletor de ordenação ────────────── */}
      <label className="text-sm flex items-center gap-2 text-zinc-300">
        <span>Ordenar por:</span>
        <select
          value={order}
          onChange={(e) => setOrder(e.target.value as SortKey)}
          className="text-xs text-white bg-zinc-800 border border-zinc-600 px-3 py-1.5 rounded-md shadow-sm hover:border-zinc-500 focus:outline-none focus:ring-1 focus:ring-lime-500 transition"

        >
          <option value="none">–</option>
          <option value="dic-asc">DIC ↑</option>
          <option value="dic-desc">DIC ↓</option>
          <option value="fic-asc">FIC ↑</option>
          <option value="fic-desc">FIC ↓</option>
        </select>
      </label>
    </div>
  );
}
