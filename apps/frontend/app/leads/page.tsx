import KpiBar           from '@/components/leads/KpiBar';
import BarPorSolucao    from '@/components/charts/BarPorSolucao';
import FunnelPorEstagio from '@/components/charts/FunnelPorEstagio';
import LineLeadsTempo   from '@/components/charts/LineLeadsTempo';
import TopLeadsTable    from '@/components/leads/TopLeadsTable';

import {
  kpis,
  porSolucao,
  porEstagio,
  serieTempo,
  topLeads,
} from '@/app/data/leads-dashboard';

export const metadata = { title: 'Leads • You.On' };

export default function LeadsPage() {
  return (
    <section className="space-y-8">
      <KpiBar kpis={kpis} />

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="rounded-xl bg-white shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Leads por solução</h2>
          <BarPorSolucao data={porSolucao} />
        </div>

        <div className="rounded-xl bg-white shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Funil por estágio</h2>
          <FunnelPorEstagio data={porEstagio} />
        </div>
      </div>

      <div className="rounded-xl bg-white shadow p-4">
        <h2 className="text-lg font-semibold mb-2">Leads por dia (últ. semana)</h2>
        <LineLeadsTempo data={serieTempo} />
      </div>

      <div className="rounded-xl bg-white shadow p-4">
        <h2 className="text-lg font-semibold mb-2">Top oportunidades</h2>
        <TopLeadsTable rows={topLeads} />
      </div>
    </section>
  );
}
