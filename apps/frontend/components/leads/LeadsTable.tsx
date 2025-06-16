'use client';
import type { Lead } from '@/app/types/lead';

export default function LeadsTable({ rows }: { rows: Lead[] }) {
  if (!rows.length) {
    return <p className="text-sm text-gray-500">Nenhum lead encontrado.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-xl border bg-white shadow">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-100 text-left">
          <tr>
            <th className="px-4 py-2">ID</th>
            <th className="px-4 py-2">Nome</th>
            <th className="px-4 py-2">Região</th>
            <th className="px-4 py-2">Solução</th>
            <th className="px-4 py-2">Status</th>
            <th className="px-4 py-2 text-right">Potencial (R$)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((l) => (
            <tr key={l.id} className="border-b last:border-0">
              <td className="px-4 py-2">{l.id}</td>
              <td className="px-4 py-2">{l.nome}</td>
              <td className="px-4 py-2">{l.regiao}</td>
              <td className="px-4 py-2">{l.solucao}</td>
              <td className="px-4 py-2 capitalize">{l.status}</td>
              <td className="px-4 py-2 text-right">
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
