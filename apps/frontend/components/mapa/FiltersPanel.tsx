'use client';
import { useFilters } from '@/store/filters';

const regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'];
const solucoes = ['Solar', 'Bateria', 'Eficiência', 'Consultoria'];

export default function FiltersPanel() {
  const { regioes: selReg, solucoes: selSol, toggleRegiao, toggleSolucao, reset } =
    useFilters();

  return (
    <aside className="w-56 bg-white shadow rounded-xl p-4 space-y-4">
      <h4 className="font-semibold">Região</h4>
      {regioes.map((r) => (
        <label key={r} className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={selReg.includes(r)}
            onChange={() => toggleRegiao(r)}
          />
          {r}
        </label>
      ))}

      <h4 className="font-semibold pt-2">Solução</h4>
      {solucoes.map((s) => (
        <label key={s} className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={selSol.includes(s)}
            onChange={() => toggleSolucao(s)}
          />
          {s}
        </label>
      ))}

      <button
        onClick={reset}
        className="text-xs text-primary hover:underline mt-2"
      >
        Limpar filtros
      </button>
    </aside>
  );
}
