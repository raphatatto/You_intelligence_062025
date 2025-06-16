import CardKPI from '@/components/ui/CardKPI';
import BarEnergy from '@/components/charts/BarEnergy';
import LineLeads from '@/components/charts/LineLeads';
import {Bolt, Users} from 'lucide-react';

import {mockEnergia} from '@/app/data/energia';
import {mockLeads}   from '@/app/data/leads';

export default function Dashboard() {
  return (
    <section className="space-y-8">
      {/* KPIs */}
      <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-6">
        <CardKPI title="Energia mapeada (MWh)" value="1 250" icon={<Bolt />} />
        <CardKPI title="Leads qualificados"      value="289"   icon={<Users />} />
      </div>

      {/* Gráficos */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="rounded-xl bg-white shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Energia mapeada por mês</h2>
          <BarEnergy data={mockEnergia} />
        </div>

        <div className="rounded-xl bg-white shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Leads por dia (últ. semana)</h2>
          <LineLeads data={mockLeads} />
        </div>
      </div>
    </section>
  );
}
