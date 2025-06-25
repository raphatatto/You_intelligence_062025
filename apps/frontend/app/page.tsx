'use client';

import CardKPI from '@/components/ui/CardKPI';
import { Bolt, Users } from 'lucide-react';
import { useLeads } from '@/services/leads';
import { countByEstado, calcularEnergiaMapeada } from '@/utils/analytics';
import BarLeadsEstado from '@/components/charts/BarLeadsEstados';

export default function Dashboard() {
  const { data: leads = [] } = useLeads();
  const dataEstado = countByEstado(leads);
  const energiaTotal = calcularEnergiaMapeada(leads);

  return (
<section className="space-y-8 px-6 lg:px-12 py-10 bg-black text-white">
  {/* Header */}
  <div className="space-y-1">
    <h1 className="text-3xl font-bold">Dashboard Interno - You.On</h1>
    <p className="text-muted-foreground text-sm">
      Mapeamento de leads e oportunidades no mercado de energia.
    </p>
  </div>

  {/* KPIs */}
  <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-6 mt-6">
    <CardKPI
      title="Energia mapeada (MWh)"
      value="17,6"
      icon={<Bolt className="text-yellow-400" />}
      className="bg-[#1a1a1a] border border-white/10"
    />
    <CardKPI
      title="Leads qualificados"
      value="4"
      icon={<Users className="text-green-400" />}
      className="bg-[#1a1a1a] border border-white/10"
    />
    <CardKPI
      title="% com CNPJ"
      value="100%"
      icon={<Users className="text-blue-400" />}
      className="bg-[#1a1a1a] border border-white/10"
    />
    <CardKPI
      title="Última atualização"
      value="25/06/2025"
      icon={<Bolt className="text-pink-400" />}
      className="bg-[#1a1a1a] border border-white/10"
    />
  </div>

  {/* Gráfico */}
  <div className="bg-[#121212] rounded-xl p-6 shadow-lg border border-white/10">
    <h2 className="text-lg font-semibold mb-3">Leads por Estado</h2>
    <BarLeadsEstado data={dataEstado} />
  </div>
</section>

  );
}
