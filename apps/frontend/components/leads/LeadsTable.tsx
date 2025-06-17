'use client';

import type { Lead } from '@/app/types/lead';
import { useRouter } from 'next/navigation';

export default function LeadsTable({ rows, selectedId }: { rows: Lead[]; selectedId?: number | null }) {
  const router = useRouter();

  if (!rows.length) {
    return <p className="text-sm text-gray-400">Nenhum lead encontrado.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-zinc-700 bg-zinc-900 shadow-lg">
      <table className="min-w-full text-sm text-zinc-200">
        <thead className="bg-zinc-800 text-zinc-400">
          <tr>
            <th className="px-4 py-3 text-left">ID</th>
            <th className="px-4 py-3 text-left">Nome</th>
            <th className="px-4 py-3 text-left">Dic</th>
            <th className="px-4 py-3 text-left">Fic</th>
            <th className="px-4 py-3 text-left">CNAE</th>
            <th className="px-4 py-3 text-left">Estado</th>
            <th className="px-4 py-3 text-left">Descrição</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((l) => (
            <tr
              key={l.id}
              onClick={() => router.push(`/mapa?id=${l.id}`)}
              className={`cursor-pointer border-b border-zinc-700 hover:bg-zinc-800 transition-all ${
                selectedId === l.id ? 'bg-zinc-800' : ''
              }`}
            >
              <td className="px-4 py-2">{l.id}</td>
              <td className="px-4 py-2">{l.nome}</td>
              <td className="px-4 py-2">{l.dicMed}</td>
              <td className="px-4 py-2">{l.ficMed}</td>
              <td className="px-4 py-2 capitalize">{l.CNAE}</td>
              <td className="px-4 py-2 uppercase">{l.estado}</td>
              <td className="px-4 py-2">{l.descricao}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
