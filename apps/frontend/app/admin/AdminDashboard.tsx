'use client';
import useSWR from 'swr';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import Link from 'next/link';

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function AdminDashboard() {
  const { data: status } = useSWR('/v1/admin/dashboard/resumo', fetcher, { refreshInterval: 5000 });
  const { data: porDistribuidora } = useSWR('/v1/admin/dashboard/distribuidora', fetcher);
  const { data: porAnoCamada } = useSWR('/v1/admin/dashboard/ano-camada', fetcher);

  return (
    <div className="space-y-12">
      {/* Ações no topo */}
      <div className="flex justify-end gap-4 mb-4">
        <Link href="/admin/importar">
          <button className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg shadow font-medium">
            📥 Ir para Importador
          </button>
        </Link>
        <Link href="/admin/enriquecer">
          <button className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg shadow font-medium">
            ⚙️ Ir para Enriquecedor
          </button>
        </Link>
      </div>

      {/* Cards resumo */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <CardResumo label="Leads RAW" valor={status?.raw || 0} cor="bg-yellow-500" />
        <CardResumo label="Parcialmente Enriquecidos" valor={status?.parcialmente_enriquecido || 0} cor="bg-blue-500" />
        <CardResumo label="Enriquecidos" valor={status?.enriquecido || 0} cor="bg-emerald-500" />
        <CardResumo label="Falhas" valor={status?.falha_enriquecer || 0} cor="bg-red-500" />
      </div>

      {/* Distribuidoras */}
      <section>
        <h2 className="text-xl font-bold text-white mb-2">📍 Leads por Distribuidora</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={porDistribuidora || []}>
            <XAxis dataKey="distribuidora" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="total_leads" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </section>

      {/* Evolução temporal */}
      <section>
        <h2 className="text-xl font-bold text-white mb-2">📅 Importações por Ano/Camada</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={porAnoCamada || []}>
            <XAxis dataKey="ano" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="UCAT" stackId="a" fill="#3b82f6" />
            <Bar dataKey="UCMT" stackId="a" fill="#f59e0b" />
            <Bar dataKey="UCBT" stackId="a" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </section>
    </div>
  );
}

function CardResumo({ label, valor, cor }: { label: string; valor: number; cor: string }) {
  return (
    <div className={`rounded-xl p-4 shadow-md text-white ${cor}`}>
      <p className="text-sm">{label}</p>
      <h3 className="text-3xl font-bold">{valor.toLocaleString()}</h3>
    </div>
  );
}
