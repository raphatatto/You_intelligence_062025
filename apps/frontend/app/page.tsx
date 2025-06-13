import CardKPI from '../components/ui/CardKPI';
import BarEnergy from '@/components/charts/BarEnergy';
import LineLeads from '@/components/charts/LineLeads';
import {Bolt, Users} from 'lucide-react';

const dadosEnergia = [
  {mes: 'Jan', mwh: 320},
  {mes: 'Fev', mwh: 280},
  {mes: 'Mar', mwh: 340},
  {mes: 'Abr', mwh: 310},
];

const dadosLeads = [
  {dia: '01', leads: 5},
  {dia: '02', leads: 8},
  {dia: '03', leads: 3},
  {dia: '04', leads: 9},
];

export default function Dashboard() {
  return (
    <section className="space-y-8">
      {/* KPIs */}
      <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-6">
        <CardKPI title="Energia mapeada (MWh)" value="1.250" icon={<Bolt />} />
        <CardKPI title="Leads qualificados" value="289" icon={<Users />} />
        {/* mais KPIs… */}
      </div>

      {/* Gráficos */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="rounded-xl bg-white shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Energia mapeada por mês</h2>
          <BarEnergy data={dadosEnergia} />
        </div>

        <div className="rounded-xl bg-white shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Leads por dia (últ. semana)</h2>
          <LineLeads data={dadosLeads} />
        </div>
      </div>
    </section>
  );
}
