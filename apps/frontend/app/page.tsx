'use client';

import CardKPI from '@/components/ui/CardKPI';
import { Bolt, Users } from 'lucide-react';
import { useLeads } from '@/services/leads';
import { countByEstado } from '@/utils/analytics';
import BarLeadsEstado from '@/components/charts/BarLeadsEstados';
import { calcularEnergiaMapeada } from '@/utils/analytics';

export default function Dashboard() {
  const { data: leads = [] } = useLeads();
  const dataEstado = countByEstado(leads);
  const energiaTotal = calcularEnergiaMapeada(leads);
  return (
    <section className="space-y-8">
      {/* KPIs */}
      <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-6">
        <CardKPI
        title="Energia mapeada (MWh)"
        value={energiaTotal.toLocaleString('pt-BR', {
          minimumFractionDigits: 1,
          maximumFractionDigits: 1,
        })}
        icon={<Bolt />}
        />
        <CardKPI title="Leads qualificados" value={leads.length.toString()} icon={<Users />} />
      </div>

      {/* Gráficos */}
      <div className="grid lg:grid-cols-1 gap-6">
        <div className="rounded-xl bg-white shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Leads por Estado</h2>
          <BarLeadsEstado data={dataEstado} />
        </div>
      </div>
    </section>
  );
}
