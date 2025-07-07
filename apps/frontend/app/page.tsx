'use client';

import CardKPI from '@/components/ui/CardKPI';
import { Bolt, Users, Zap } from 'lucide-react';
import { useLeads } from '@/services/leads';
import { countByEstado, calcularEnergiaMapeada } from '@/utils/analytics';
import BarLeadsDistribuidora from '@/components/charts/BarLeadsDistribuidora';
import { countByDistribuidora } from '@/utils/analytics';
import BarTopCNAE from '@/components/charts/BarTopCNAE';
import { top10CNAE } from '@/utils/analytics';
import { filtrarLeadsComPotencial } from '@/utils/analytics';


export default function Dashboard() {
  const { leads = [], isLoading, error } = useLeads(); // ✅ certo
  const dataEstado = countByEstado(leads);
  const energiaTotal = calcularEnergiaMapeada(leads).toFixed(1); ;
  const dataCNAE = top10CNAE(leads);
  const totalLeads = leads.length;
  const leadsPotenciais = filtrarLeadsComPotencial(leads, 100);
  const totalPotenciais = leadsPotenciais.length;


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
      title="Total de Leads"
      value={totalLeads.toLocaleString('pt-BR')}
      icon={<Users className="text-cyan-400" />}
      className="bg-[#1a1a1a] border border-white/10"
    />
    <CardKPI
      title="Última atualização"
      value="04/07/2025"
      icon={<Bolt className="text-pink-400" />}
      className="bg-[#1a1a1a] border border-white/10"
    />
  </div>

  {/* Gráfico */}
  <div className="bg-[#121212] rounded-xl p-6 shadow-lg border border-white/10">
  <h2 className="text-lg font-semibold mb-3">Leads por Distribuidora</h2>
  <BarLeadsDistribuidora data={countByDistribuidora(leads)} />
  </div>
  <div className="bg-[#121212] rounded-xl p-6 shadow-lg border border-white/10">
  <h2 className="text-lg font-semibold mb-3">Top 10 CNAEs mais frequentes</h2>
  <BarTopCNAE data={dataCNAE} />
  </div>
</section>

  );
}
