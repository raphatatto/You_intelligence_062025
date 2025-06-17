// components/leads/FiltersBar.tsx
'use client';

import { useFilters } from '@/store/filters'; // ← só UF
import { useSort, SortKey } from '@/store/sort'; // ← ordenação

export default function FiltersBar({ estados }: { estados: string[] }) {
  /* estado (UF) */
  const { estado, setEstado } = useFilters();

  /* ordenação DIC / FIC */
  const { order, setOrder } = useSort();

  return (
    <div className="flex flex-wrap gap-6 bg-white p-4 rounded-xl shadow">
      {/* ────────────── seletor de UF ────────────── */}
      <label className="text-sm flex items-center gap-2">
        <span>Estado:</span>
        <select
          value={estado}
          onChange={(e) => setEstado(e.target.value)}
          className="border rounded px-2 py-1"
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
      <label className="text-sm flex items-center gap-2">
        <span>Ordenar por:</span>
        <select
          value={order}
          onChange={(e) => setOrder(e.target.value as SortKey)}
          className="border rounded px-2 py-1"
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
