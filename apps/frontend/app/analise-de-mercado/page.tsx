// app/analise-de-mercardo/page.tsx
'use client'

import { BarChart4, Zap, Battery, Droplet, Wind, Sun, Activity, Flame } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs'
import { MarketOverview } from '@/components/market/MarketOverview'
import { PriceTrends } from '@/components/market/PriceTrends'
import { GenerationSources } from '@/components/market/GenerationSources'
import { RegionalAnalysis } from '@/components/market/RegionAnalysis'

export default function MarketAnalysisPage() {
  return (
    <div className="flex flex-col h-full">
      {/* Cabeçalho */}
      <header className="border-b border-gray-700 p-6">
        <div className="flex items-center gap-4">
          <BarChart4 className="text-blue-400" size={28} />
          <div>
            <h1 className="text-2xl font-bold text-white">Análise de Mercado Energético</h1>
            <p className="text-gray-400">Dados atualizados em tempo real do setor energético</p>
          </div>
        </div>
      </header>

      {/* Indicadores-chave */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-6 border-b border-gray-700">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">Preço Médio</CardTitle>
            <Zap className="h-4 w-4 text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ 350,20</div>
            <p className="text-xs text-green-400 mt-1">+2.4% em 30 dias</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">Demanda Total</CardTitle>
            <Activity className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">45.230 MW</div>
            <p className="text-xs text-green-400 mt-1">+1.1% em 30 dias</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">Capacidade Instalada</CardTitle>
            <Battery className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">78.450 MW</div>
            <p className="text-xs text-green-400 mt-1">+5.3% no último ano</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">Participação Renovável</CardTitle>
            <Sun className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">62%</div>
            <p className="text-xs text-red-400 mt-1">-3.2% em relação ao ano passado</p>
          </CardContent>
        </Card>
      </section>

      {/* Conteúdo principal */}
      <main className="flex-1 overflow-auto p-6">
        <Tabs defaultValue="overview" className="h-full">
          <TabsList className="grid w-full grid-cols-4 bg-gray-900">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <Flame size={16} /> Visão Geral
            </TabsTrigger>
            <TabsTrigger value="prices" className="flex items-center gap-2">
              <Zap size={16} /> Preços
            </TabsTrigger>
            <TabsTrigger value="generation" className="flex items-center gap-2">
              <Droplet size={16} /> Geração
            </TabsTrigger>
            <TabsTrigger value="regional" className="flex items-center gap-2">
              <Wind size={16} /> Regional
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-4">
            <MarketOverview />
          </TabsContent>

          <TabsContent value="prices" className="mt-4">
            <PriceTrends />
          </TabsContent>

          <TabsContent value="generation" className="mt-4">
            <GenerationSources />
          </TabsContent>

          <TabsContent value="regional" className="mt-4">
            <RegionalAnalysis />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}