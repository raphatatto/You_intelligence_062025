// app/detetive/page.tsx
'use client'

import { Flame, Search, Bell, Settings } from 'lucide-react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs'
import DetectivePanel from '@/components/detective/Panel'
import MarketOverview from '@/components/detective/MarketOverview'
import NewsFeed from '@/components/detective/NewsFeed'
import ReportsList from '@/components/detective/ReportsList'
import { useDetective } from '@/contexts/DetectiveContext'

export default function DetectivePage() {
  const { activeFeature, setActiveFeature } = useDetective()

  return (
    <div className="flex flex-col h-full">
      {/* Cabeçalho */}
      <header className="border-b border-gray-700 p-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Flame className="text-orange-400" size={28} />
            <h1 className="text-2xl font-bold text-white">
              Detetive de Mercado Energético
            </h1>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="p-2 rounded-full hover:bg-gray-800">
              <Search className="text-gray-400 hover:text-white" size={20} />
            </button>
            <button className="p-2 rounded-full hover:bg-gray-800 relative">
              <Bell className="text-gray-400 hover:text-white" size={20} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
          </div>
        </div>

        {/* Filtros rápidos */}
        <div className="mt-6 flex gap-3 overflow-x-auto pb-2">
          {['Todos', 'Solar', 'Eólica', 'Hidrelétrica', 'Gás Natural', 'Nuclear'].map((tag) => (
            <button
              key={tag}
              className="px-4 py-1.5 text-sm rounded-full bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white whitespace-nowrap"
            >
              {tag}
            </button>
          ))}
        </div>
      </header>

      {/* Conteúdo principal */}
      <main className="flex-1 overflow-hidden p-6">
        <Tabs defaultValue="overview" className="h-full flex flex-col">
          <TabsList className="grid w-full grid-cols-4 bg-gray-900">
            <TabsTrigger value="overview" className="py-3">
              Visão Geral
            </TabsTrigger>
            <TabsTrigger value="news" className="py-3">
              Notícias
            </TabsTrigger>
            <TabsTrigger value="reports" className="py-3">
              Relatórios
            </TabsTrigger>
            <TabsTrigger value="alerts" className="py-3">
              Alertas
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="flex-1 overflow-auto mt-4">
            <MarketOverview />
          </TabsContent>

          <TabsContent value="news" className="flex-1 overflow-auto mt-4">
            <NewsFeed />
          </TabsContent>

          <TabsContent value="reports" className="flex-1 overflow-auto mt-4">
            <ReportsList />
          </TabsContent>

          <TabsContent value="alerts" className="flex-1 overflow-auto mt-4">
            <div className="bg-gray-900/50 rounded-lg p-6 text-center">
              <Settings className="mx-auto text-gray-600 mb-2" size={24} />
              <h3 className="text-lg font-medium text-gray-300">
                Alertas e Configurações
              </h3>
              <p className="text-gray-500 mt-1">
                Configure seus alertas personalizados aqui
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </main>

      {/* Painel do Detetive */}
      <DetectivePanel />
    </div>
  )
}