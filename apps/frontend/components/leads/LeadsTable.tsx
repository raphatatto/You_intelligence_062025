'use client';
import type { Lead } from '@/app/types/lead';
import { useRouter } from 'next/navigation';

export default function LeadsTable({ rows, selectedId }: { rows: Lead[]; selectedId?: number | null; } ) {
  const router = useRouter();
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
            <th className="px-4 py-2">Dic</th>
            <th className="px-4 py-2">Fic</th>
            <th className="px-4 py-2">CNAE</th>
            <th className="px-4 py-2">Estado</th>
            <th className="px-4 py-2">Descrição</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((l) => (
            <tr key={l.id} className="border-b last:border-0 cursor-pointer hover:bg-gray-50" onClick={() => router.push(`/mapa?id=${l.id}`)} >
              <td className="px-4 py-2">{l.id}</td>
              <td className="px-4 py-2">{l.nome}</td>
              <td className="px-4 py-2">{l.dicMed}</td>
              <td className="px-4 py-2">{l.ficMed}</td>
              <td className="px-4 py-2 capitalize">{l.CNAE}</td>
              <td className="px-4 py-2 capitalize">{l.estado}</td>
              <td className="px-4 py-2 capitalize">{l.descricao}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
