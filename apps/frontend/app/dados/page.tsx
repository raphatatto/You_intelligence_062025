import CardKPI              from '@/components/ui/CardKPI';
import GaugeQualidade       from '@/components/charts/GaugeQualidade';
import BarEnriquecimento    from '@/components/charts/BarEnriquecimento';
import LineQualidadeTrend   from '@/components/charts/LineQualidadeTrend';
import AlertsList           from '@/components/dados/AlertsList';

import {
  kpis,
  gaugeQualidade,
  enriquecimento,
  serieQualidade,
  alerts,
} from '@/app/data/dados-dashboard';
import { TrendingUp } from 'lucide-react';

export const metadata = { title: 'Dados • You.On' };

export default function DadosPage() {
  return (
    <section className="space-y-8">
      {/* KPIs */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        { kpis.map(k => (
        <CardKPI
            key={k.label}
            title={k.label}
            value={String(k.valor)}
            icon={<TrendingUp />}       
        />
        )) }
      </div>

      {/* Gauge + Enriquecimento */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="rounded-xl bg-white shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Qualidade geral</h2>
          <GaugeQualidade valor={gaugeQualidade} />
        </div>

        <div className="rounded-xl bg-white shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Cobertura de atributos</h2>
          <BarEnriquecimento data={enriquecimento} />
        </div>
      </div>

      {/* Tendência */}
      <div className="rounded-xl bg-white shadow p-4">
        <h2 className="text-lg font-semibold mb-2">Evolução da qualidade (%)</h2>
        <LineQualidadeTrend data={serieQualidade} />
      </div>

      {/* Alertas */}
      <div className="rounded-xl bg-white shadow p-4">
        <h2 className="text-lg font-semibold mb-2">Alertas de dados</h2>
        <AlertsList items={alerts} />
      </div>
    </section>
  );
}
