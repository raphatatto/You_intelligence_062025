// app/dashboard/page.jsx
'use client';
import CardKPI from '@/components/ui/CardKPI';
import { Bolt, Users, RefreshCw, Calendar } from 'lucide-react';
import { useLeads } from '@/services/leads';
import {calcularEnergiaMapeada, countByDistribuidora, top10CNAE, filtrarLeadsComPotencial } from '@/utils/analytics';
import BarLeadsDistribuidora from '@/components/charts/BarLeadsDistribuidora';
import BarTopCNAE from '@/components/charts/BarTopCNAE';
import EnergiaMensalChart from '@/components/charts/EnergiaMensalChart';
import DemandaMensalChart from '@/components/charts/DemandaMensalChart';
import DICFICMensalChart from '@/components/charts/DICFICMensalChart';
import { gerarDadosMensais } from '@/utils/transformarDadosMensais';

export default function Dashboard() {
  const { leads = [], isLoading, error } = useLeads();
  if (error) return <div className="text-red-400 p-8">Erro ao carregar os dados.</div>;
  if (isLoading) return <div className="text-zinc-400 p-8">Carregando dados...</div>;

  const totalLeads = leads.length;
  const energiaTotal = calcularEnergiaMapeada(leads).toFixed(1);
  const leadsPotenciais = filtrarLeadsComPotencial(leads, 100);
  const totalPotenciais = leadsPotenciais.length;

  const dataDistribuidora = countByDistribuidora(leads);
  const dataCNAE = top10CNAE(leads);


  const { energia_mensal, demanda_mensal, dic_fic_mensal } = gerarDadosMensais(leads);

  return (
    <section className="space-y-6 px-4 lg:px-8 py-6 bg-black text-white min-h-screen">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
            Dashboard Interno - You.On
          </h1>
          <p className="text-zinc-400 text-sm">
            Mapeamento de leads e oportunidades no mercado de energia
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-zinc-400 bg-zinc-900/70 px-3 py-2 rounded-lg border border-zinc-800">
          <RefreshCw className="w-4 h-4" />
          <span>Atualizado em: 20/08/2025</span>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <CardKPI
          title="Total de Leads"
          value={totalLeads.toLocaleString('pt-BR')}
          icon={<Users className="w-5 h-5 text-green-400" />}
          trend="up"
          trendValue="12%"
        />
        <CardKPI
          title="Leads com Potencial"
          value={totalPotenciais.toLocaleString('pt-BR')}
          icon={<Bolt className="w-5 h-5 text-green-400" />}
          trend="up"
          trendValue="8%"
        />
        <CardKPI
          title="Energia Mapeada"
          value={`${energiaTotal} kWh`}
          icon={<Bolt className="w-5 h-5 text-green-400" />}
          trend="up"
          trendValue="15%"
        />
        <CardKPI
          title="Última Atualização"
          value="04/07/2025"
          icon={<Calendar className="w-5 h-5 text-green-400" />}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Leads por Distribuidora */}
        <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-5 shadow-lg hover:shadow-green-500/10 transition-all">
          <div className="flex justify-between items-center mb-4">
            <span className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded-full">
              {dataDistribuidora.length} distribuidoras
            </span>
          </div>
          <div className="h-[350px]">
            <BarLeadsDistribuidora data={dataDistribuidora} />
          </div>
        </div>
        
        {/* Top CNAEs */}
        <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-5 shadow-lg hover:shadow-green-500/10 transition-all">
          <div className="flex justify-between items-center mb-4">
            <span className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded-full">
              Segmentos mais frequentes
            </span>
          </div>
          <div className="h-[350px]">
            <BarTopCNAE data={dataCNAE} />
          </div>
        </div>

        {/* Consumo de Energia */}
        <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-5 shadow-lg hover:shadow-green-500/10 transition-all">
          <div className="flex justify-between items-center mb-4">
            <span className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded-full">
              Últimos 12 meses
            </span>
          </div>
          <div className="h-[350px]">
            <EnergiaMensalChart data={energia_mensal} />
          </div>
        </div>

        {/* Demanda Mensal */}
        <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-5 shadow-lg hover:shadow-green-500/10 transition-all">
          <div className="flex justify-between items-center mb-4">
            <span className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded-full">
              kW médios
            </span>
          </div>
          <div className="h-[350px]">
            <DemandaMensalChart data={demanda_mensal} />
          </div>
        </div>

        {/* DIC e FIC */}
        <div className="lg:col-span-2 bg-zinc-900/70 border border-zinc-800 rounded-xl p-5 shadow-lg hover:shadow-green-500/10 transition-all">
          <div className="flex justify-between items-center mb-4">
            <div className="flex gap-2">
              <span className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded-full">
                DIC (min)
              </span>
              <span className="text-xs bg-cyan-900/30 text-cyan-400 px-2 py-1 rounded-full">
                FIC (vezes)
              </span>
            </div>
          </div>
          <div className="h-[350px]">
            <DICFICMensalChart data={dic_fic_mensal} />
          </div>
        </div>
      </div>
    </section>
  );
}