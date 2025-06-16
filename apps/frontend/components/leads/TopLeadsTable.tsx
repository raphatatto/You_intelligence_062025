'use client';
import type { LeadRow } from '@/app/types/leads-dashboard';

export default function TopLeadsTable({ rows }: { rows: LeadRow[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-3 py-2 text-left">Nome</th>
            <th className="px-3 py-2">Solução</th>
            <th className="px-3 py-2">Estágio</th>
            <th className="px-3 py-2 text-right">Potencial (R$)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id} className="border-b">
              <td className="px-3 py-2">{r.nome}</td>
              <td className="px-3 py-2 text-center">{r.solucao}</td>
              <td className="px-3 py-2 text-center capitalize">{r.estagio}</td>
              <td className="px-3 py-2 text-right">{r.potencial.toLocaleString('pt-BR')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
